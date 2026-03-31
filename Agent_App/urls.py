from django.urls import path
from rest_framework import routers
from .api import (
    AutoViewSet, 
    AgenteChatView, 
    BuscarAutosView, 
    CambiarEstadoAutoView, 
    BuscarClientesView,  
    EliminarClienteView,
    ResetChatView,
    ObtenerHistorialChatView   
)
from .autos import AutosWebhookView
from .clientes import ClientesWebhookView

router = routers.DefaultRouter()
router.register(r"api/Agent_App", AutoViewSet, "Agent_App")

urlpatterns = [
    path("api/chat/", AgenteChatView.as_view(), name="agente-chat"),
    path("webhooks/autos/", AutosWebhookView.as_view(), name="webhook-autos"),
    path("webhooks/clientes/", ClientesWebhookView.as_view(), name="webhook-clientes"),
    
    path("api/buscar-autos/", BuscarAutosView.as_view(), name="buscar-autos"),
    path("api/autos/<int:pk>/cambiar-estado/", CambiarEstadoAutoView.as_view(), name="cambiar-estado-auto"),

    path("api/buscar-clientes/", BuscarClientesView.as_view(), name="buscar-clientes"),
    path("api/clientes/<int:pk>/eliminar/", EliminarClienteView.as_view(), name="eliminar-cliente"),
    path('api/chat/reset/', ResetChatView.as_view(), name='chat-reset'),
    path('api/chat/historial/', ObtenerHistorialChatView.as_view(), name='historial_chat'),
]

urlpatterns += router.urls