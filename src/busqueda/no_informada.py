import heapq
from collections import deque
from typing import Callable

from .interfaz import AlgoritmoBusqueda


def _ruta(padres, inicio, objetivo):
    if objetivo not in padres:
        return []
    resultado = []
    actual = objetivo
    while actual != inicio:
        resultado.append(actual)
        actual = padres[actual]
    resultado.reverse()
    return resultado


class _BusquedaPrioridad(AlgoritmoBusqueda):
    """Base de búsquedas que priorizan estados por un valor numérico."""

    def __init__(self, prioridad: Callable):
        self._prioridad = prioridad

    def planificar(self, agente, entorno, agentes):
        inicio = tuple(agente.posicion)
        objetivo = entorno.salida
        if objetivo is None or inicio == objetivo:
            return []

        costos = {inicio: 0.0}
        padres = {inicio: None}
        cola = [(self._valor_prioridad(0.0, inicio, objetivo), 0, inicio)]
        contador = 0
        while cola:
            prioridad, _, actual = heapq.heappop(cola)
            costo = costos[actual]
            if prioridad != self._valor_prioridad(costo, actual, objetivo):
                continue
            if actual == objetivo:
                return _ruta(padres, inicio, objetivo)
            for vecino in entorno.vecinos(actual):
                vecino = tuple(vecino)
                nuevo = costo + entorno.costo_movimiento(vecino)
                if nuevo < costos.get(vecino, float("inf")):
                    costos[vecino] = nuevo
                    padres[vecino] = actual
                    contador += 1
                    heapq.heappush(
                        cola,
                        (self._valor_prioridad(nuevo, vecino, objetivo),
                         contador, vecino),
                    )
        return []

    def _valor_prioridad(self, costo, posicion, objetivo):
        return self._prioridad(costo, posicion, objetivo)


class BFS(AlgoritmoBusqueda):

    def planificar(self, agente, entorno, agentes):
        inicio = tuple(agente.posicion)
        objetivo = entorno.salida

        if objetivo is None:
            return []

        if inicio == objetivo:
            return []

        cola = deque([inicio])
        padre = {inicio: None}

        while cola:
            actual = cola.popleft()

            if actual == objetivo:
                return self._reconstruir_ruta(padre, inicio, objetivo)

            for vecino in entorno.vecinos(actual):
                vecino = tuple(vecino)

                if vecino in padre:
                    continue

                padre[vecino] = actual
                cola.append(vecino)

        return []

    @staticmethod
    def _reconstruir_ruta(padre, inicio, objetivo):
        ruta = []
        actual = objetivo

        while actual != inicio:
            ruta.append(actual)
            actual = padre[actual]

        ruta.reverse()
        return ruta


class BusquedaCostoUniforme(_BusquedaPrioridad):
    """Búsqueda no informada que minimiza el costo acumulado."""

    def __init__(self):
        super().__init__(lambda costo, posicion, objetivo: costo)
