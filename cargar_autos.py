import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Test_Agent_Api_Rest.settings')
django.setup()

from Agent_App.models import Auto

autos = [
    ("Superdeportivo", "Bugatti", "Chiron Super Sport", "Azul Atlántico", 3800000000, 2024),
    ("Superdeportivo", "Lamborghini", "Revuelto", "Arancio Apodis", 600000000, 2024),
    ("Superdeportivo", "Ferrari", "SF90 Stradale", "Rosso Corsa", 520000000, 2024),
    ("Lujo", "Rolls-Royce", "Phantom", "Graphite", 460000000, 2026),
    ("Lujo", "Bentley", "Continental GT", "British Racing Green", 240000000, 2024),
    ("Deportivo", "Porsche", "911 Turbo S", "Plata Twin-Turbo", 230000000, 2024),
    ("Eléctrico", "Audi", "RS e-tron GT", "Gris Daytona", 147000000, 2026),
    ("Sedán", "BMW", "M5 CS", "Frozen Deep Green", 140000000, 2026),
    ("Sedán", "Mercedes-Benz", "Clase S 580", "Negro Obsidiana", 125000000, 2024),
    ("SUV", "Land Rover", "Range Rover Sport", "Santorini Black", 110000000, 2024),
    ("Eléctrico", "Tesla", "Model X Plaid", "Blanco Perla", 95000000, 2024),
    ("Lujo", "Lexus", "LS 500", "Sonic Quartz", 80000000, 2023),
    ("Pick-up", "Ford", "F-150 Raptor", "Azul Antimateria", 78000000, 2024),
    ("SUV", "Volvo", "XC90 Recharge", "Crystal White", 72000000, 2024),
    ("SUV", "Jeep", "Grand Cherokee", "Bright White", 45000000, 2026),
    ("SUV", "Toyota", "RAV4 Hybrid", "Lunar Rock", 35000000, 2024),
    ("SUV", "Honda", "CR-V", "Meteorite Gray", 33000000, 2026),
    ("SUV", "Mazda", "CX-5", "Soul Red Crystal", 30000000, 2024),
    ("Sedán", "Hyundai", "Elantra", "Cyber Gray", 22000000, 2024),
    ("Sedán", "Volkswagen", "Jetta", "Platinum Grey", 21500000, 2026),
    ("Sedán", "Kia", "Forte", "Snow White Pearl", 20000000, 2026),
    ("Sedán", "Nissan", "Versa", "Electric Blue", 17000000, 2024),
    ("Hatchback", "Chevrolet", "Spark", "Summit White", 15000000, 2024),
    ("Hatchback", "Suzuki", "Swift", "Pure White", 14500000, 2025),
    ("Hatchback", "Dacia", "Sandero", "Glacier White", 11000000, 2025),
]

def cargar_datos():
    for tipo, marca, modelo, color, precio, ano in autos:
        Auto.objects.create(
            Tipo=tipo,
            Marca=marca,
            Modelo=modelo,
            Color=color,
            Precio=precio,
            Ano=ano,
            Estado=True
        )
    print(f"¡Éxito! Se cargaron {len(autos)} autos a la base de datos.")

if __name__ == '__main__':
    cargar_datos()