from abc import ABC, abstractmethod


class AlgoritmoBusqueda(ABC):
    """Contrato común para los algoritmos de evacuación."""

    @abstractmethod
    def planificar(self, agente, entorno, agentes):
        """Devuelve una ruta de posiciones, sin incluir la posición actual."""
        raise NotImplementedError
