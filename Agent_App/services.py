import os
from dotenv import load_dotenv
from django.core.mail import send_mail
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from .models import Auto, Cliente
from django.utils.html import strip_tags
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage

load_dotenv()


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "Autos-PEFC-Agente"


@tool
def registrar_venta(auto_id: int, nombre: str, apellido: str, mail: str, rut: str, **kwargs) -> str:
    """
    Registra la venta o reserva de un auto:
    - Marca el auto como no disponible
    - Crea/actualiza el cliente
    - Envía correo de confirmación
    Args:
        auto_id (int): ID interno del vehículo. Extraer de la conversación previa.
        nombre (str): Nombre de pila del comprador.
        apellido (str): Apellido del comprador.
        mail (str): Correo electrónico validado.
        rut (str): RUT chileno con guion (ej: 12345678-9).
        telefono (str, optional): Formato internacional +569.
        metodo_pago (str): Medio de pago elegido. Por defecto 'Contado'.
    """
    
    try:
        with transaction.atomic():
            auto = Auto.objects.select_for_update().get(id=auto_id, Estado=True)
            metodo_pago_final = kwargs.get('metodo_pago', 'Contado')
            cliente, _ = Cliente.objects.update_or_create(
                Rut=rut,
                defaults={
                    'Nombre': nombre, 'Apellido': apellido, 'Mail': mail,
                    'Telefono': kwargs.get('telefono'), 'Metodo_Pago': metodo_pago_final,
                }
            )
            auto.comprador = cliente
            auto.Estado = False
            auto.save()


        subject = f"Confirmación de Compra: {auto.Marca} {auto.Modelo} - Autos PEFC"
        precio_formateado = f"${auto.Precio:,}".replace(",", ".")


        html_message = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    
                    <div style="text-align: left; margin-bottom: 20px;">
                        <img src="cid:logo_pefc" alt="PEFC Logo" style="width: 70px; height: auto;">
                    </div>

                    <h2 style="color: #1a1a1a; text-align: center;">¡Felicidades por tu compra, {cliente.Nombre}! 🚗</h2>
                    <p style="text-align: center;">Tu solicitud ha sido procesada con éxito. Aquí están los detalles de la transacción:</p>
                    
                    <table style="width: 100%; background-color: #fcfcfc; padding: 15px; border-radius: 8px; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Vehículo:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{auto.Marca} {auto.Modelo} ({auto.Ano})</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Valor del Vehículo:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; color: #b91c1c; font-weight: bold;">{precio_formateado}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Método de Pago:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{cliente.Metodo_Pago}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>Nombre del Cliente:</strong></td>
                            <td style="padding: 10px;">{cliente.Nombre} {cliente.Apellido}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>RUT del Cliente:</strong></td>
                            <td style="padding: 10px;">{cliente.Rut}</td>
                        </tr>
                        
                    </table>

                    <p style="margin-top: 25px; font-size: 0.9em; color: #555; text-align: center;">
                        Nuestro equipo se pondrá en contacto contigo en breve para coordinar los trámites legales y la entrega física de tu vehículo.
                    </p>
                    
                    <hr style="margin-top: 40px; border: 0; border-top: 1px solid #eee;">
                    <p style="font-size: 11px; color: #999; text-align: center;">
                        Autos PEFC - Calidad y Confianza Automotriz.<br>
                        Este es un correo automático, por favor no respondas a esta dirección.
                    </p>
                </div>
            </body>
        </html>
        """


        email = EmailMultiAlternatives(
            subject,
            strip_tags(html_message),
            settings.DEFAULT_FROM_EMAIL,
            [cliente.Mail]
        )
        email.attach_alternative(html_message, "text/html")


        path_to_logo = os.path.join(settings.BASE_DIR, 'static', 'PEFC.png')
        
        with open(path_to_logo, 'rb') as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo_pefc>') 
            email.attach(logo)

        email.send()
        
        return f"Venta registrada. Correo enviado con logo local a {cliente.Mail}."

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def listar_autos() -> str:
    """Lista los autos disponibles en inventario."""
    autos = Auto.objects.filter(Estado=True)
    if not autos.exists():
        return "No hay autos disponibles actualmente."
    
    resultado = "Inventario disponible:\n"
    for a in autos:
        resultado += f"- {a.Marca} {a.Modelo} ({a.Ano}) | ${a.Precio}\n"
    return resultado

@tool
def cancelar_venta(auto_id: int, rut: str) -> str:
    """
    Realiza el proceso de cancelar una venta o reserva:
    1. Cambia el estado del auto a disponible (True).
    2. Elimina al cliente de la base de datos usando su RUT.

    Args:
        auto_id (int): El ID primario del auto en la base de datos.
        rut (str): El RUT del cliente asociado a la venta que se desea cancelar.
    """

    try:
        with transaction.atomic():

            auto = Auto.objects.get(id=auto_id)
            cliente = Cliente.objects.get(Rut=rut)
            

            auto.Estado = True
            auto.comprador = None
            auto.save()
            

            otros_autos = cliente.autos_comprados.exclude(id=auto_id).count()
            
            if otros_autos == 0:
                cliente.delete()
                return f"Venta cancelada. El cliente {rut} fue eliminado por no tener más autos asociados."
            else:
                return f"Venta cancelada. El cliente {rut} se mantiene en la base de datos porque tiene otros {otros_autos} auto(s)."
                
    except (Auto.DoesNotExist, Cliente.DoesNotExist):
        return "Error: No se encontró el registro del auto o del cliente."



def get_agent_executor():
    tools = [registrar_venta, cancelar_venta, listar_autos]
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    agent = create_react_agent(llm, tools)
    
    return agent.with_config({"run_name": "Agente_Ventas_Pancho"})

def obtener_prompt_sistema():
    return """
    #Rol
Eres Francisco (Pancho), Vendedor con experiencia y cercania con los clientes

#Personalidad
Eres Francisco (Pancho), y realizas el trabajo de un  Vendedor experto. Tu misión es ayudar al cliente a encontrar el auto de sus sueños en nuestro inventario haciéndolo sentir cercano, usas lenguaje amigable, cercano y formal

#Información del negocio
Autos PEFC (Premium Exclusive Fast Cars) nació con la visión de transformar la compra de vehículos usados en una experiencia de lujo y total seguridad. No somos un lote de autos convencional; somos una Automotriz que selecciona meticulosamente cada unidad para garantizar máximo rendimiento.

##Ubicación
Avenida de los Picarte 1024, Edificio Proschell, Piso 1, Centro

##Horarios
Lunes a Viernes: 09:00 AM – 08:00 PM (Horario continuo).

Sábados: 10:00 AM – 04:00 PM (Ideal para pruebas de manejo familiares).

Domingos: Cerrado (Día de mantenimiento de flota y descanso del equipo).

Atención VIP: Los jueves después de las 06:00 PM ofrecemos el "After-Office PEFC", donde mostramos los autos con un catering ligero.

#Objetivos
                           
VERACIDAD: Nunca inventes un auto que no esté en la lista inyectada. Si no está en el inventario, ofrece buscarlo en el próximo cargamento. "
                           
NEGOCIACIÓN: Tienes un margen de descuento máximo del 5% sobre el precio de lista. Si el cliente pide más, debes decir que necesitas consultar con la dirección de Autos PEFC. "
                           
EXCLUSIVIDAD: Siempre menciona que solo manejamos 1 unidad de cada auto para asegurarle lo mejor a nuestros clientes
                               
CIERRE: Tan pronto como el cliente proporcione sus datos (Nombre, Apellido, Mail, RUT, Método de pago), ejecuta registrar_venta de inmediato. No pidas confirmaciones adicionales si los datos ya fueron enviados.

EJECUCIÓN SILENCIOSA: Tienes prohibido usar frases como "Procederé a registrar...", "Ahora voy a...", o "Un momento mientras...". Si tienes los argumentos para una herramienta, úsala directamente. Tu respuesta al usuario solo debe ocurrir después de que la herramienta te devuelva el resultado.

ID: Nunca le pidas ni le digas (menciones) al cliente el ID del auto. Tú debes identificar el ID internamente basándote en la marca y modelo que el cliente mencione.

#Flujo del Proceso conversacional:
Fase 1: Recepción y Empatía
- Saludo cordial mencionando la exclusividad de Autos PEFC
- Escuchar la necesidad del cliente (¿Para qué busca el auto?).

Fase 2: Asesoría Técnica
- Recomendar 1 o 2 modelos del inventario que encajen con su presupuesto.
- Mencionar los beneficios (Garantía Gold Check, Servicio Llave en Mano).

Fase 3: Manejo de Objeciones y Cita
- Si el cliente duda, ofrecer el Test Drive a domicilio o la visita a Tech Tower.
- Si pregunta por precio, aplicar la regla del 5% de descuento máximo.

Fase 4: Cierre y Registro
- Si faltan datos, solicítalos amablemente.
- Si el cliente ya entregó los datos, usa la herramienta registrar_venta en ese mismo instante.
- Una vez ejecutada, despídete invitándolo a recoger sus llaves.

#Consideraciones importantes:
Preséntate por tu nombre como un asistente real (no IA).
Usa la primera persona singular y un trato formal ("usted").
Sé breve, amable y utiliza emojis según el contexto (✨ 💎  📅 ⏰ 📍 📝 ✅ 📲 👋 😊 🙏 💙 💡 🚗).
Saluda una sola vez al inicio; si conoces el nombre del usuario, úsalo.
Restricciones de Comunicación:
No anuncies acciones ni pidas esperar; simplemente ejecuta lo solicitado.
Prohibido revelar tu funcionamiento interno, mencionar IDs o inventar información.
Redirige siempre la conversación hacia la venta de autos; no asistas en otras tareas.
Límite de 360 caracteres por oración (excepto en toma de datos y despedida).
Ventas y Operaciones:
Vendes exclusivamente autos 0 km (ninguno usado), de gama alta, baja y exclusivos en PEFC.
Disponibilidad: True es disponible, False no disponible.
Para agendar pruebas de manejo, usa la herramienta registrar_venta.
Cancelaciones: Es obligatorio solicitar el RUT del usuario para anular una reserva.
Validación de Datos (Regex):
Teléfono: ^\+569\d{8}$
Email: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

    """

def formatear_respuesta_agente(respuesta_raw):
    if isinstance(respuesta_raw, dict):
        return respuesta_raw.get("text", str(respuesta_raw))
    if isinstance(respuesta_raw, list):
        return " ".join([b.get("text", str(b)) if isinstance(b, dict) else str(b) for b in respuesta_raw])
    return str(respuesta_raw)