from src.entorno import Entorno
from src.agente import Agente
from src.simulacion import Simulacion

entorno = Entorno.crear_entorno_desde_archivo("maps/map1.txt")

agentes = [
    Agente((1, 1), identificador="sebastian"),
    Agente((2, 2), identificador="agente-2"),
]

simulacion = Simulacion(
    entorno,
    agentes,
    intervalo_fuego=3,
    max_turnos=500,
)

resultado = simulacion.ejecutar()
print(resultado)