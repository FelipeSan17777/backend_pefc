import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Test_Agent_Api_Rest.settings')
django.setup()

from Agent_App.models import Cliente


clientes = [
    ("Santi", "Giménez", "santi.g@gmail.com", "+56911111111", "18234567-k", "Crédito"),
    ("María", "Pinto", "m.pinto@outlook.com", "+56922222222", "15443221-5", "Débito"),
    ("Carlos", "Ruiz", "cruiz@yahoo.cl", "+56933333333", "19554332-2", "Transferencia"),
    ("Valentina", "Silva", "val.silva@gmail.com", "+56944444444", "20112334-1", "Efectivo"),
    ("Joaquín", "Soto", "j.soto@empresa.com", "+56955555555", "17665443-8", "Crédito"),
    ("Isabel", "Allende", "i.allende@gmail.com", "+56966666666", "12887665-4", "Débito"),
    ("Andrés", "Bello", "abello@educacion.cl", "+56977777777", "9443556-2", "Transferencia"),
    ("Francisca", "Valenzuela", "fran.v@musica.cl", "+56988888888", "21998776-k", "Crédito"),
    ("Diego", "Portales", "dportales@gob.cl", "+56999999999", "11332445-7", "Efectivo"),
    ("Lucía", "Hiriart", "lucia.h@mail.com", "+56912345678", "14223112-3", "Débito"),
    ("Gabriel", "Mistral", "g.mistral@poesia.cl", "+56987654321", "8554332-k", "Transferencia"),
    ("Roberto", "Bolaño", "r.bolano@literatura.com", "+56954321678", "13778990-2", "Crédito"),
    ("Camila", "Vallejo", "c.vallejo@politica.cl", "+56943218765", "18665443-4", "Débito"),
    ("Esteban", "Paredes", "e.paredes@gol.cl", "+56932187654", "16554332-1", "Transferencia"),
    ("Alexis", "Sánchez", "as7@wonder.com", "+56921876543", "17443221-9", "Crédito"),
    ("Arturo", "Vidal", "king@vidal.cl", "+56918765432", "16223445-0", "Efectivo"),
    ("Claudio", "Bravo", "c.bravo@porteria.cl", "+56909876543", "15112334-7", "Transferencia"),
    ("Daniela", "Vega", "d.vega@cine.cl", "+56922334455", "19332445-k", "Crédito"),
    ("Pedro", "Pascal", "p.pascal@hollywood.com", "+56933445566", "14887665-2", "Débito"),
    ("Mon", "Laferte", "mon.l@art.cl", "+56944556677", "20554332-8", "Transferencia"),
    ("Jorge", "González", "j.gonzalez@prisioneros.cl", "+56955667788", "13112334-5", "Efectivo"),
    ("Anita", "Tijoux", "a.tijoux@rap.com", "+56966778899", "17445667-3", "Crédito"),
    ("Benjamín", "Vicuña", "b.vicuna@actor.cl", "+56977889900", "15998776-1", "Débito"),
    ("Javiera", "Mena", "j.mena@pop.cl", "+56988990011", "18223445-6", "Transferencia"),
    ("Gonzalo", "Valenzuela", "g.valenzuela@actor.cl", "+56999001122", "16112334-9", "Crédito"),
]

def cargar_clientes():
    for nombre, apellido, mail, telefono, rut, pago in clientes:
        Cliente.objects.create(
            Nombre=nombre,
            Apellido=apellido,
            Mail=mail,
            Telefono=telefono,
            Rut=rut,
            Metodo_Pago=pago
        )
    print(f"¡Éxito! Se cargaron {len(clientes)} clientes a la base de datos.")

if __name__ == '__main__':
    cargar_clientes()