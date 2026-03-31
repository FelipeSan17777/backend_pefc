from rest_framework import serializers
from .models import Auto, Cliente



class AutoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auto
        fields = ("id", "Tipo", "Marca", "Modelo", "Color", "Precio", "Ano", "Estado")

class AutoWebhookSerializer(AutoSerializer):

    pass


class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = '__all__'

class ClienteWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            "id", "Nombre", "Apellido", "Mail", 
            "Telefono", "Rut", "Metodo_Pago"
        ]