from django.db import models

class Cliente(models.Model):
    Nombre = models.CharField(max_length=30, null=False)
    Apellido = models.CharField(max_length=50, null=False)
    Mail = models.EmailField(null=True)
    Telefono = models.CharField(max_length=12, null=True)
    Rut = models.CharField(max_length=10)
    Metodo_Pago = models.CharField(max_length=20, null=False)

    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"

class Auto(models.Model):
    Tipo = models.CharField(max_length=20)
    Marca = models.CharField(max_length=50)
    Modelo = models.CharField(max_length=100)
    Color = models.CharField(max_length=30)
    Precio = models.IntegerField()
    Ano = models.PositiveBigIntegerField()
    Estado = models.BooleanField(default=True) 
    
    comprador = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="autos_comprados"
    )

    def __str__(self):
        return f"{self.Marca} {self.Modelo} ({self.Ano})"

class EstadoConversacion(models.Model):
    session_id = models.CharField(max_length=100)
    fase = models.CharField(max_length=50, default="inicio") 
    mensajes = models.TextField(blank=True, null=True)      
    actualizado = models.DateTimeField(auto_now=True)       