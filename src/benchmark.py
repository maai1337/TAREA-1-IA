import argparse
import csv
import random
import statistics
from collections import deque
from pathlib import Path

import numpy as np

from .agente import Agente
from .busqueda import (
    AEstrella,
    AlgoritmoGenetico,
    BFS,
    BusquedaCostoUniforme,
    BusquedaVoraz,
)
from .entorno import TipoCelda, Entorno
from .simulacion import Simulacion


ALGORITMOS = {
    "BFS": BFS,
    "Costo uniforme": BusquedaCostoUniforme,
    "A*": AEstrella,
    "Greedy Best-First": BusquedaVoraz,
    "Genético": AlgoritmoGenetico,
}
SEMILLA = 1


def _crear_entorno(mapa, rng, fuegos):
    entorno = Entorno.crear_entorno_desde_archivo(mapa, capacidad_celda=3)
    libres = [
        tuple(int(valor) for valor in posicion)
        for posicion in np.argwhere(entorno.grilla == TipoCelda.LIBRE)
    ]
    for posicion in rng.sample(libres, min(fuegos, len(libres))):
        entorno.grilla[posicion] = TipoCelda.FUEGO
    return entorno


def _zona_grupo(entorno, cantidad, rng):
    libres = [
        tuple(int(valor) for valor in posicion)
        for posicion in np.argwhere(entorno.grilla == TipoCelda.LIBRE)
    ]
    rng.shuffle(libres)
    for centro in libres:
        cola = deque([centro])
        visitados = {centro}
        posiciones = []
        while cola and len(posiciones) < cantidad:
            actual = cola.popleft()
            posiciones.append(actual)
            for vecino in entorno.vecinos(actual):
                vecino = tuple(vecino)
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)
        if len(posiciones) >= cantidad:
            return posiciones
    raise ValueError(
        f"No existe una zona conectada con {cantidad} posiciones libres."
    )


def _crear_agentes(entorno, cantidad, rng):
    posiciones = _zona_grupo(entorno, cantidad, rng)
    return [
        Agente(posicion, identificador=f"agente-{indice}")
        for indice, posicion in enumerate(posiciones)
    ]


def _algoritmo(nombre, semilla):
    if nombre == "Genético":
        return Genetico(
            poblacion=12,
            generaciones=12,
            max_pasos=120,
            semilla=semilla,
        )
    return ALGORITMOS[nombre]()


def ejecutar_benchmark(
    iteraciones,
    cantidad_agentes,
    cantidad_fuegos,
):
    raiz = Path("maps")
    salida = Path("resultados")
    salida.mkdir(parents=True, exist_ok=True)
    mapas = sorted(raiz.glob("map*.txt"))
    if not mapas:
        raise FileNotFoundError(f"No hay mapas map*.txt en {raiz}.")

    filas = []
    for mapa in mapas:
        for nombre in ALGORITMOS:
            supervivencias = []
            despejes = []
            bajas = []
            for iteracion in range(iteraciones):
                rng = random.Random(SEMILLA + iteracion)
                entorno = _crear_entorno(mapa, rng, cantidad_fuegos)
                agentes = _crear_agentes(entorno, cantidad_agentes, rng)
                algoritmo = _algoritmo(nombre, SEMILLA + iteracion)
                resultado = Simulacion(
                    entorno,
                    agentes,
                    algoritmo=algoritmo,
                    intervalo_fuego=3,
                    max_turnos=150,
                ).ejecutar()
                supervivencias.append(resultado["tasa_supervivencia"])
                bajas.append(resultado["bajas"])
                if resultado["tiempo_despeje"] is not None:
                    despejes.append(resultado["tiempo_despeje"])

            filas.append({
                "mapa": mapa.stem,
                "algoritmo": nombre,
                "iteraciones": iteraciones,
                "agentes": cantidad_agentes,
                "fuegos_iniciales": cantidad_fuegos,
                "supervivencia_media": statistics.mean(supervivencias),
                "supervivencia_std": statistics.stdev(supervivencias)
                if len(supervivencias) > 1 else 0.0,
                "tiempo_despeje_media": statistics.mean(despejes)
                if despejes else "",
                "tiempo_despeje_std": statistics.stdev(despejes)
                if len(despejes) > 1 else 0.0,
                "tiempo_despeje_min": min(despejes) if despejes else "",
                "tiempo_despeje_max": max(despejes) if despejes else "",
                "bajas_medias": statistics.mean(bajas),
            })

    csv_path = salida / "benchmark_resumen.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=filas[0].keys())
        escritor.writeheader()
        escritor.writerows(filas)

    _generar_graficos(filas, salida)
    return csv_path


def _generar_graficos(filas, directorio):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    mapas = sorted({fila["mapa"] for fila in filas})
    algoritmos = list(ALGORITMOS)
    for metrica, etiqueta, nombre_archivo in [
        ("supervivencia_media", "Tasa de supervivencia media", "supervivencia"),
        ("tiempo_despeje_media", "Tiempo medio de despeje (turnos)", "despeje"),
    ]:
        figura, eje = plt.subplots(figsize=(11, 6))
        ancho = 0.8 / len(algoritmos)
        posiciones = np.arange(len(mapas))
        for indice, algoritmo in enumerate(algoritmos):
            valores = [
                next(
                    fila[metrica] for fila in filas
                    if fila["mapa"] == mapa and fila["algoritmo"] == algoritmo
                ) or 0
                for mapa in mapas
            ]
            eje.bar(
                posiciones + indice * ancho,
                valores,
                ancho,
                label=algoritmo,
            )
        eje.set_xticks(posiciones + ancho * (len(algoritmos) - 1) / 2)
        eje.set_xticklabels(mapas)
        eje.set_ylabel(etiqueta)
        eje.set_title(f"Comparación por mapa: {etiqueta}")
        eje.legend()
        figura.tight_layout()
        figura.savefig(directorio / f"benchmark_{nombre_archivo}.png", dpi=160)
        plt.close(figura)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteraciones", type=int, required=True)
    parser.add_argument("--agentes", type=int, required=True)
    parser.add_argument("--fuegos", type=int, required=True)
    argumentos = parser.parse_args()
    print(f"Resultados guardados en {ejecutar_benchmark(
        argumentos.iteraciones,
        argumentos.agentes,
        argumentos.fuegos,
    )}")
