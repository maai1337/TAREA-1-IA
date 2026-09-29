# TAREA-1-IA

## Requisitos

- Python 3.10 o superior.
- `numpy`.
- `matplotlib` para generar los gráficos.

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```


## Benchmark

El benchmark se ejecuta desde la raíz del repositorio, la configuracion usada 
para la entrega fue la siguiente:

```powershell
python -m src.benchmark `
    --iteraciones 200 `
    --agentes 80 `
    --fuegos 3 `
```

Los argumentos del benchmark se indican explícitamente:

- `--iteraciones`: cantidad de repeticiones.
- `--agentes`: cantidad de agentes.
- `--fuegos`: cantidad de focos iniciales de fuego.


El benchmark ejecuta las 15 combinaciones de mapas y algoritmos, y genera:

- `resultados/benchmark_resumen.csv`.
- `resultados/benchmark_supervivencia.png`.
- `resultados/benchmark_despeje.png`.

El CSV contiene, por combinación:

- tasa media y desviación estándar de supervivencia;
- tiempo medio y desviación estándar de despeje;
- tiempo mínimo y máximo de despeje;
- promedio de bajas.
