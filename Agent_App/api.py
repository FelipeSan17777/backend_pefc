import json
import unicodedata
import re 
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Auto, Cliente, EstadoConversacion
from .serializers import AutoSerializer, ClienteSerializer
from .services import get_agent_executor, obtener_prompt_sistema, formatear_respuesta_agente



def construir_regex_busqueda(texto):
    if not texto: return ""

    texto_limpio = re.escape(texto)
    texto_base = ''.join(c for c in unicodedata.normalize('NFD', texto_limpio.lower()) if unicodedata.category(c) != 'Mn')
    mapa_vocales = {'a': '[aá]', 'e': '[eé]', 'i': '[ií]', 'o': '[oó]', 'u': '[uúü]'}
    patron = "".join(mapa_vocales.get(letra, letra) for letra in texto_base)
    return patron



class BuscarClientesView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        queryset = Cliente.objects.all()
        search = request.query_params.get('search')
        
        if search:
            for palabra in search.split():
                patron = construir_regex_busqueda(palabra)
                queryset = queryset.filter(
                    Q(Nombre__iregex=patron) | 
                    Q(Apellido__iregex=patron) |
                    Q(Mail__iregex=patron) |
                    Q(Telefono__iregex=patron) |
                    Q(Rut__iregex=patron)
                )
        return Response(ClienteSerializer(queryset, many=True).data)

class BuscarAutosView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        queryset = Auto.objects.all()
        search = request.query_params.get('search')
        precio_min = request.query_params.get('precio_min')
        precio_max = request.query_params.get('precio_max')

        if search:
            for palabra in search.split():
                patron = construir_regex_busqueda(palabra)
                queryset = queryset.filter(
                    Q(Marca__iregex=patron) | 
                    Q(Modelo__iregex=patron) |
                    Q(Tipo__iregex=patron) |
                    Q(Color__iregex=patron)
                )
        

        try:
            if precio_min:
                queryset = queryset.filter(Precio__gte=float(precio_min))
            if precio_max:
                queryset = queryset.filter(Precio__lte=float(precio_max))
        except (ValueError, TypeError):
            pass 

        return Response(AutoSerializer(queryset, many=True).data)



class AgenteChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        comentario = request.data.get("comentario")
        
        if not comentario or not comentario.strip():
            return Response({"error": "El mensaje no puede estar vacío"}, status=400)

        if not request.session.session_key:
            request.session.create()
        
        estado, _ = EstadoConversacion.objects.get_or_create(
            session_id=request.session.session_key,
            defaults={"fase": "inicio", "mensajes": "[]"}
        )


        contexto_db = "Inventario de Autos PEFC (Top 25):\n"
        for a in Auto.objects.all()[:25]: 
            estado_texto = "Disponible" if a.Estado else "Vendido/Reservado"
            contexto_db += f"- ID: {a.id} | {a.Marca} {a.Modelo} | ${a.Precio} | Estado: {estado_texto}\n"

        messages = [("system", f"{obtener_prompt_sistema()}\nInformación en tiempo real:\n{contexto_db}")]

        try:
            historial = json.loads(estado.mensajes) if estado.mensajes else []
            if not isinstance(historial, list): historial = []
        except (json.JSONDecodeError, TypeError):
            historial = []

        for msg in historial[-10:]:
            role = "human" if msg.get("role") in ["user", "human"] else "ai"
            messages.append((role, msg.get("content", "")))
        
        messages.append(("human", comentario))


        try:
            agent = get_agent_executor()
            result = agent.invoke({"messages": messages})
            

            respuesta_texto = ""

            for msg in reversed(result["messages"]):

                content = getattr(msg, 'content', '')
                if content and not getattr(msg, 'tool_calls', None):
                    respuesta_texto = formatear_respuesta_agente(content)
                    break
            

            if not respuesta_texto:
                respuesta_texto = "He procesado tu solicitud con éxito. ¿Deseas algo más?"


            historial.extend([
                {"role": "user", "content": comentario},
                {"role": "ai", "content": respuesta_texto}
            ])
            estado.mensajes = json.dumps(historial)
            estado.save()

            return Response({"respuesta": respuesta_texto})

        except Exception as e:
            print(f"ERROR EN AGENTE: {e}") 
            return Response({"error": "Error interno del asistente", "detalle": str(e)}, status=500)

class ResetChatView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        if not request.session.session_key:
            return Response({"status": "no_history", "mensaje": "No hay sesión activa"})
        
        EstadoConversacion.objects.filter(session_id=request.session.session_key).update(
            mensajes="[]", 
            fase="inicio"
        )
        
        return Response({
            "mensaje": "Historial de chat reseteado correctamente.",
            "status": "reset_success"
        })

class ObtenerHistorialChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        
        try:
            estado = EstadoConversacion.objects.get(session_id=request.session.session_key)
            
            try:
                mensajes = json.loads(estado.mensajes) if estado.mensajes else []
                if not isinstance(mensajes, list): mensajes = []
            except (json.JSONDecodeError, TypeError):
                mensajes = []

            historial = [
                {
                    "text": msg.get("content", ""),
                    "sender": "user" if msg.get("role") in ["human", "user"] else "ai"
                } for msg in mensajes
            ]
            return Response({"historial": historial}, status=200)
        
        except EstadoConversacion.DoesNotExist:
            return Response({"historial": []}, status=200)

class AutoViewSet(viewsets.ModelViewSet):
    queryset = Auto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = AutoSerializer

class EliminarClienteView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk):
        try:
            cliente = Cliente.objects.get(pk=pk)
            nombre_completo = f"{cliente.Nombre} {cliente.Apellido}"
            

            cliente.autos_comprados.all().update(
                comprador=None, 
                Estado=True
            )

            cliente.delete()
            
            return Response({
                "mensaje": f"Cliente {nombre_completo} eliminado con éxito. Los vehículos asociados han sido devueltos al inventario."
            }, status=200)

        except Cliente.DoesNotExist:
            return Response({"error": "Cliente no encontrado."}, status=404)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=500)

class CambiarEstadoAutoView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            auto = Auto.objects.get(pk=pk)
            

            nuevo_estado = request.data.get('nuevo_estado')

            if nuevo_estado is not None:

                auto.Estado = bool(nuevo_estado)
            else:

                auto.Estado = not auto.Estado


            auto.save()
            estado_texto = "Disponible" if auto.Estado else "No disponible"
            
            return Response({
                "mensaje": f"Estado de {auto.Marca} actualizado.",
                "nuevo_estado": auto.Estado,
                "descripcion": estado_texto
            }, status=200)
        except Auto.DoesNotExist:
            return Response({"error": "Auto no encontrado."}, status=404)