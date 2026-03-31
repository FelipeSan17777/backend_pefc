from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def cargar_datos_iniciales(sender, **kwargs):

    if sender.name != "tu_app":
        return

    from .cargar_autos import cargar_autos
    from .cargar_clientes import cargar_clientes

    cargar_autos()
    cargar_clientes()
