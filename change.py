import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Test_Agent_Api_Rest.settings')
django.setup()

from Agent_App.models import Auto

def desactivar_auto(auto_id):
    # .update() es más eficiente que .save() porque ejecuta una sola sentencia SQL UPDATE
    filas_actualizadas = Auto.objects.filter(id=auto_id).update(Estado=True)
    
    if filas_actualizadas:
        print(f"Éxito: El auto con ID {auto_id} ahora no está disponible (Estado=False).")
    else:
        print(f"Error: No se encontró ningún auto con ID {auto_id}.")

if __name__ == "__main__":
    desactivar_auto(1)