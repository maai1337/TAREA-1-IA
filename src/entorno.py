from enum import IntEnum
from pathlib import Path
import numpy as np

class TipoCelda(IntEnum):
    LIBRE = 0
    MURO = 1
    FUEGO = 2
    SALIDA = 3

class Entorno:
    def __init__(self, grilla, salida, capacidad_celda=1):
        if grilla.ndim != 2 or grilla.size == 0:
            raise ValueError("La grilla debe ser una matriz bidimensional no vacía.")
        if capacidad_celda < 1:
            raise ValueError("La capacidad de cada celda debe ser positiva.")
        if salida is None:
            raise ValueError("El entorno debe tener una salida.")
        self.grilla = grilla
        self.ocupacion = np.zeros_like(grilla, dtype=int)
        self.salida = tuple(salida)
        self.capacidad_celda = capacidad_celda

    @property
    def posiciones_fuego(self):
        return set(map(tuple, np.argwhere(self.grilla == TipoCelda.FUEGO)))

    def vecinos(self, pos, incluir_espera=False):
        fila, col = pos
        candidatos = [(fila - 1, col), (fila + 1, col),
                      (fila, col - 1), (fila, col + 1)]
        if incluir_espera:
            candidatos.append((fila, col))
        return [p for p in candidatos if self.es_transitable(p)]

    def es_transitable(self, pos):
        fila, col = pos
        dentro = 0 <= fila < self.grilla.shape[0] and 0 <= col < self.grilla.shape[1]
        return dentro and self.grilla[fila, col] != TipoCelda.MURO and self.grilla[fila, col] != TipoCelda.FUEGO

    def actualizar_ocupacion(self, agentes_vivos):
        self.ocupacion[:] = 0
        for agente in agentes_vivos:
            self.ocupacion[agente.posicion] += 1

    def costo_movimiento(self, pos):
        if not self.es_transitable(pos):
            return float("inf")
        ocupacion = self.ocupacion[pos]
        return 1 + (ocupacion / self.capacidad_celda) ** 2

    def propagar_fuego(self):
        nuevas = set()
        for fila, col in self.posiciones_fuego:
            for vecino in ((fila - 1, col), (fila + 1, col),
                           (fila, col - 1), (fila, col + 1)):
                f, c = vecino
                dentro = 0 <= f < self.grilla.shape[0] and 0 <= c < self.grilla.shape[1]
                if dentro and self.grilla[f, c] in (TipoCelda.LIBRE, TipoCelda.SALIDA):
                    nuevas.add(vecino)
        for pos in nuevas:
            self.grilla[pos] = TipoCelda.FUEGO
        return nuevas

    @staticmethod
    def crear_entorno_desde_archivo(ruta_archivo, capacidad_celda=1):
        ruta = Path(ruta_archivo)
        if not ruta.exists():
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")
        
        with open(ruta, 'r', encoding='utf-8') as f:
            lineas = [linea.strip() for linea in f if linea.strip()]
        if not lineas:
            raise ValueError("El archivo del mapa está vacío.")
        ancho = len(lineas[0])
        if any(len(linea) != ancho for linea in lineas):
            raise ValueError("Todas las filas del mapa deben tener el mismo ancho.")
        
        grilla = []
        salida = None
        salidas = 0
        
        for fila_idx, linea in enumerate(lineas):
            fila = []
            for col_idx, char in enumerate(linea):
                if char == '0':
                    fila.append(TipoCelda.LIBRE)
                elif char == '1':
                    fila.append(TipoCelda.MURO)
                elif char == '2':
                    fila.append(TipoCelda.FUEGO)
                elif char == '3':
                    fila.append(TipoCelda.SALIDA)
                    salida = (fila_idx, col_idx)
                    salidas += 1
                else:
                    raise ValueError(
                        f"Caracter inválido {char!r} en la posición "
                        f"({fila_idx}, {col_idx})"
                    )

            grilla.append(fila)
        if salidas != 1:
            raise ValueError("El mapa debe contener exactamente una salida '3'.")
        return Entorno(np.array(grilla, dtype=TipoCelda), salida, capacidad_celda)