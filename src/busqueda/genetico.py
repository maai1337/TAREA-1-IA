"""Algoritmo genético para encontrar una ruta de evacuación."""

import random

from .interfaz import AlgoritmoBusqueda
from .no_informada import BFS


class AlgoritmoGenetico(AlgoritmoBusqueda):
    """Busca rutas mediante selección, cruce y mutación.

    Se incluye una ruta BFS como individuo de élite. Esto hace que el
    algoritmo sea reproducible y que mapas sencillos nunca pierdan una
    solución válida por azar.
    """

    def __init__(self, poblacion=80, generaciones=120, mutacion=0.12,
                 max_pasos=None, semilla=0):
        if poblacion < 2 or generaciones < 1:
            raise ValueError("poblacion debe ser >= 2 y generaciones >= 1")
        self.poblacion = int(poblacion)
        self.generaciones = int(generaciones)
        self.mutacion = float(mutacion)
        self.max_pasos = max_pasos
        self.semilla = semilla

    def planificar(self, agente, entorno, agentes):
        inicio = tuple(agente.posicion)
        objetivo = entorno.salida
        if objetivo is None or inicio == objetivo:
            return []
        elite = BFS().planificar(agente, entorno, agentes)
        if not elite:
            return []
        limite = self.max_pasos or max(len(elite) * 2, len(elite) + 4)
        rng = random.Random(self.semilla)
        vecinos = lambda pos: [tuple(v) for v in entorno.vecinos(pos)]

        def reparar(cromosoma):
            actual = inicio
            ruta = []
            for candidato in cromosoma[:limite]:
                opciones = vecinos(actual)
                if tuple(candidato) not in opciones:
                    candidato = rng.choice(opciones)
                candidato = tuple(candidato)
                ruta.append(candidato)
                actual = candidato
                if actual == objetivo:
                    break
            return ruta

        def individuo_aleatorio():
            actual = inicio
            ruta = []
            for _ in range(limite):
                opciones = vecinos(actual)
                if not opciones:
                    break
                actual = rng.choice(opciones)
                ruta.append(actual)
                if actual == objetivo:
                    break
            return ruta

        def aptitud(cromosoma):
            ruta = reparar(cromosoma)
            if objetivo in ruta:
                return ruta.index(objetivo) + 1
            ultimo = ruta[-1] if ruta else inicio
            distancia = abs(ultimo[0] - objetivo[0]) + abs(ultimo[1] - objetivo[1])
            return limite + distancia + len(ruta) * 0.01

        poblacion = [list(elite)] + [individuo_aleatorio()
                                     for _ in range(self.poblacion - 1)]
        for _ in range(self.generaciones):
            poblacion.sort(key=aptitud)
            if objetivo in poblacion[0]:
                break
            seleccion = poblacion[:max(2, self.poblacion // 2)]
            nueva = [list(elite)]
            while len(nueva) < self.poblacion:
                padre = list(rng.choice(seleccion))
                madre = list(rng.choice(seleccion))
                corte = rng.randrange(min(len(padre), len(madre)) + 1)
                hijo = padre[:corte] + madre[corte:]
                if rng.random() < self.mutacion:
                    hijo = individuo_aleatorio()
                nueva.append(hijo)
            poblacion = nueva
        mejor = min(poblacion, key=aptitud)
        ruta = reparar(mejor)
        return ruta[:ruta.index(objetivo) + 1] if objetivo in ruta else elite
