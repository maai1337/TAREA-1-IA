import heapq

from .agente import EstadoAgente
from .busqueda.interfaz import AlgoritmoBusqueda


class Simulacion:
    def __init__(self, entorno, agentes, algoritmo=None, intervalo_fuego=1,
                 max_turnos=1000):
        self.entorno = entorno
        self.agentes = list(agentes)
        self.algoritmo = algoritmo
        self.intervalo_fuego = intervalo_fuego
        self.max_turnos = max_turnos
        self.turno = 0
        self.finalizada = False
        self.historial = []
        self._validar_agentes()
        self.entorno.actualizar_ocupacion(self.agentes_activos)

    @property
    def agentes_activos(self):
        return [a for a in self.agentes if a.activo]

    @property
    def agentes_evacuados(self):
        return [a for a in self.agentes if a.evacuado]

    @property
    def agentes_baja(self):
        return [a for a in self.agentes if a.estado == EstadoAgente.BAJA]

    @property
    def tasa_supervivencia(self):
        return len(self.agentes_evacuados) / len(self.agentes) if self.agentes else 1.0

    @property
    def tiempo_despeje(self):
        tiempos = [a.turno_evacuacion for a in self.agentes_evacuados]
        return max(tiempos) if tiempos else None

    def _validar_agentes(self):
        if len({id(a) for a in self.agentes}) != len(self.agentes):
            raise ValueError("La lista no puede contener el mismo agente dos veces.")
        for agente in self.agentes:
            if not self.entorno.es_transitable(agente.posicion):
                raise ValueError(f"Posición inicial no transitable: {agente.posicion}")
            agente.turno_inicio = self.turno
            if agente.posicion == self.entorno.salida:
                agente.evacuar(self.turno)

    def _planificar(self, agente):
        if self.algoritmo is None:
            return self._ruta_corta(agente.posicion)
        if not isinstance(self.algoritmo, AlgoritmoBusqueda):
            raise TypeError(
                "El algoritmo debe heredar de AlgoritmoBusqueda e implementar "
                "planificar(agente, entorno, agentes)."
            )
        resultado = self.algoritmo.planificar(
            agente, self.entorno, self.agentes
        )
        if resultado is None:
            ruta = []
        elif isinstance(resultado, tuple) and len(resultado) == 2:
            ruta = [tuple(resultado)]
        else:
            ruta = [tuple(pos) for pos in resultado]
        return ruta

    def _ruta_corta(self, inicio):
        if self.entorno.salida is None:
            return []
        cola = [(0, inicio)]
        costos = {inicio: 0}
        anterior = {inicio: None}
        while cola:
            costo_actual, actual = heapq.heappop(cola)
            if costo_actual != costos[actual]:
                continue
            if actual == self.entorno.salida:
                ruta = []
                while actual != inicio:
                    ruta.append(actual)
                    actual = anterior[actual]
                return list(reversed(ruta))
            for vecino in self.entorno.vecinos(actual):
                nuevo_costo = costo_actual + self.entorno.costo_movimiento(vecino)
                if nuevo_costo < costos.get(vecino, float("inf")):
                    costos[vecino] = nuevo_costo
                    anterior[vecino] = actual
                    heapq.heappush(cola, (nuevo_costo, vecino))
        return []

    def _movimiento_valido(self, origen, destino):
        if destino == origen:
            return True
        return destino in self.entorno.vecinos(origen)

    def paso(self):
        if self.finalizada:
            return False
        if not self.agentes_activos:
            self.finalizada = True
            return False

        self.entorno.actualizar_ocupacion(self.agentes_activos)
        propuestas = {}
        for agente in self.agentes_activos:
            ruta = self._planificar(agente)
            destino = ruta[0] if ruta else agente.posicion
            if not self._movimiento_valido(agente.posicion, destino):
                raise ValueError(
                    f"El algoritmo propuso un movimiento inválido: "
                    f"{agente.posicion} -> {destino}")
            propuestas[agente] = destino

        destinos = {}
        for agente, destino in propuestas.items():
            destinos.setdefault(destino, []).append(agente)
        movimientos = {}
        for destino, candidatos in destinos.items():
            disponibles = max(0, self.entorno.capacidad_celda -
                              self.entorno.ocupacion[destino])
            quietos = [a for a in candidatos if destino == a.posicion]
            entrantes = [a for a in candidatos if destino != a.posicion]
            permitidos = quietos + entrantes[:disponibles]
            for agente in permitidos:
                movimientos[agente] = destino
            for agente in entrantes[disponibles:]:
                movimientos[agente] = agente.posicion

        self.turno += 1
        for agente in self.agentes_activos:
            agente.posicion = movimientos[agente]
        self.entorno.actualizar_ocupacion(self.agentes_activos)

        for agente in list(self.agentes_activos):
            if agente.posicion == self.entorno.salida:
                agente.evacuar(self.turno)

        nuevas_llamas = set()
        if self.turno % self.intervalo_fuego == 0:
            nuevas_llamas = self.entorno.propagar_fuego()
        for agente in self.agentes_activos:
            if agente.posicion in nuevas_llamas or not self.entorno.es_transitable(agente.posicion):
                agente.registrar_baja(self.turno)

        self.entorno.actualizar_ocupacion(self.agentes_activos)
        self.historial.append({
            "turno": self.turno,
            "evacuados": len(self.agentes_evacuados),
            "bajas": len(self.agentes_baja),
            "activos": len(self.agentes_activos),
            "fuego_nuevo": len(nuevas_llamas),
        })
        self.finalizada = not self.agentes_activos
        return True

    def ejecutar(self):
        while self.agentes_activos and self.turno < self.max_turnos:
            self.paso()
        self.finalizada = not self.agentes_activos or self.turno >= self.max_turnos
        return self.resultado()

    def resultado(self):
        return {
            "turnos": self.turno,
            "sobrevivientes": len(self.agentes_evacuados),
            "bajas": len(self.agentes_baja),
            "activos": len(self.agentes_activos),
            "tasa_supervivencia": self.tasa_supervivencia,
            "tiempo_despeje": self.tiempo_despeje,
        }