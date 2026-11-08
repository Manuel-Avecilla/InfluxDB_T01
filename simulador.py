"""
Simulador de telemetría de red para la práctica
«Análisis en tiempo real de dos routers con InfluxDB».

Escribe en InfluxDB 3 (database "sensores") la measurement "trafico_raw" con:
  - tag   : device        -> router1 | router2
  - fields: traffic_in    (Mbps, float)
            traffic_out   (Mbps, float)
            latency       (ms, float)

Detalles pensados para poder resolver todas las consultas del enunciado:
  * Ambos routers se escriben con el MISMO timestamp en cada ciclo (útil para
    comparar/unir lecturas).
  * Una lectura por segundo por router (por defecto): hay datos de sobra para
    "último minuto", "últimos 10 s", ventanas de 10 s, etc.
  * La latencia es ~normal con picos ocasionales (anomalías), de modo que el
    filtro "latency > media + 2·desviación" devuelve filas.
  * Todos los fields se escriben siempre como float (evita conflictos de tipo).
  * --backfill N rellena los últimos N minutos de histórico al arrancar, para
    tener datos de 5 minutos desde el primer momento.

Requisitos:  pip install influxdb3-python
Uso:
  python simulador.py                 # envío continuo cada 1 s
  python simulador.py --backfill 10   # primero 10 min de histórico, luego continuo
"""

import argparse
import math
import os
import random
import time
from datetime import datetime, timedelta, timezone

from influxdb_client_3 import InfluxDBClient3, Point

# --- Conexión (InfluxDB 3 Core: se usa "database" en lugar de "bucket") -----
HOST = os.getenv("INFLUX_HOST", "http://localhost:8181")
TOKEN = os.getenv("INFLUX_TOKEN", "apiv3_iot_pruebas_token_super_seguro_1234567890")
DATABASE = os.getenv("INFLUX_DATABASE", "sensores")

MEASUREMENT = "trafico_raw"

# Perfil de cada router (tráfico base en Mbps y latencia media en ms)
ROUTERS = {
    "router1": {"base_in": 120.0, "base_out": 80.0, "lat_mean": 15.0},
    "router2": {"base_in": 60.0, "base_out": 150.0, "lat_mean": 22.0},
}

SPIKE_PROB = 0.04  # probabilidad de pico de latencia (anomalía) por lectura


def sample(profile: dict, t: float) -> tuple[float, float, float]:
    """Devuelve (traffic_in, traffic_out, latency) para el instante t (segundos)."""
    # Onda lenta (periodo 2 min) + ruido para que el tráfico "respire"
    wave = 1.0 + 0.3 * math.sin(2 * math.pi * t / 120.0)
    t_in = max(0.0, profile["base_in"] * wave * random.gauss(1.0, 0.08))
    t_out = max(0.0, profile["base_out"] * wave * random.gauss(1.0, 0.08))

    # Latencia normal; más tráfico -> ligeramente más latencia
    lat = random.gauss(profile["lat_mean"] + 0.02 * t_in, 3.0)
    if random.random() < SPIKE_PROB:
        lat = random.uniform(60.0, 120.0)  # pico anómalo
    lat = max(1.0, lat)

    return round(float(t_in), 2), round(float(t_out), 2), round(float(lat), 2)


def build_points(ts: datetime, t: float) -> list[Point]:
    """Un punto por router, con el mismo timestamp."""
    points = []
    for device, profile in ROUTERS.items():
        t_in, t_out, lat = sample(profile, t)
        points.append(
            Point(MEASUREMENT)
            .tag("device", device)
            .field("traffic_in", t_in)
            .field("traffic_out", t_out)
            .field("latency", lat)
            .time(ts)
        )
    return points


def backfill(client: InfluxDBClient3, minutes: int, interval: float) -> None:
    """Escribe histórico de los últimos `minutes` minutos, en lotes."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=minutes)
    steps = int(minutes * 60 / interval)
    batch: list[Point] = []
    for i in range(steps):
        ts = start + timedelta(seconds=i * interval)
        batch.extend(build_points(ts, ts.timestamp()))
        if len(batch) >= 1000:
            client.write(record=batch)
            batch = []
    if batch:
        client.write(record=batch)
    print(f"Histórico escrito: {steps} lecturas por router ({minutes} min).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de dos routers para InfluxDB 3")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="segundos entre lecturas (por defecto 1)")
    parser.add_argument("--backfill", type=int, default=0,
                        help="minutos de histórico a generar al arrancar (por defecto 0)")
    args = parser.parse_args()

    with InfluxDBClient3(host=HOST, token=TOKEN, database=DATABASE) as client:
        if args.backfill > 0:
            backfill(client, args.backfill, args.interval)

        print(f"Enviando telemetría a '{DATABASE}.{MEASUREMENT}' cada {args.interval}s "
              "(Ctrl+C para detener)")
        try:
            while True:
                ts = datetime.now(timezone.utc)
                points = build_points(ts, ts.timestamp())
                try:
                    client.write(record=points)
                    print(f"{ts:%H:%M:%S} -> {len(points)} puntos escritos (router1, router2)")
                except Exception as exc:  # no tumbar el simulador por un fallo puntual
                    print(f"Error al escribir: {exc}")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nSimulación finalizada.")


if __name__ == "__main__":
    main()