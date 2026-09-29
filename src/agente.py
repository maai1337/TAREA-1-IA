from enum import Enum


class EstadoAgente(str, Enum):
    ACTIVO = "activo"
    EVACUADO = "evacuado"
    BAJA = "baja"


class Agente:
    def __init__(self, posicion, estado=EstadoAgente.ACTIVO, identificador=None):
        self.posicion = tuple(posicion)
        self.estado = EstadoAgente(estado)
        self.identificador = identificador
        self.ruta = []
        self.turno_inicio = None
        self.turno_evacuacion = None
        self.turno_baja = None

    @property
    def activo(self):
        return self.estado == EstadoAgente.ACTIVO

    @property
    def evacuado(self):
        return self.estado == EstadoAgente.EVACUADO

    @property
    def sobrevivio(self):
        return self.evacuado

    def evacuar(self, turno):
        self.estado = EstadoAgente.EVACUADO
        self.turno_evacuacion = turno
        self.ruta.clear()

    def registrar_baja(self, turno):
        self.estado = EstadoAgente.BAJA
        self.turno_baja = turno
        self.ruta.clear()
