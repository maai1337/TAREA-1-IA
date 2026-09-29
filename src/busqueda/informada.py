"""Búsquedas informadas mediante heurísticas."""

from .no_informada import _BusquedaPrioridad


def _distancia(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class AEstrella(_BusquedaPrioridad):
    """A* con distancia Manhattan como heurística admisible."""

    def __init__(self):
        super().__init__(
            lambda costo, posicion, objetivo:
            costo + _distancia(posicion, objetivo)
        )


class BusquedaVoraz(_BusquedaPrioridad):
    """Greedy Best-First Search, ordenada únicamente por h(n)."""

    def __init__(self):
        super().__init__(
            lambda costo, posicion, objetivo:
            _distancia(posicion, objetivo)
        )
