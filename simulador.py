import os
import time
import random
from influxdb_client_3 import InfluxDBClient3, Point

# InfluxDB 3 Core: no hay organizacion; se usa "database" en lugar de "bucket"
HOST = "http://localhost:8181"
TOKEN = os.getenv("INFLUX_TOKEN", "apiv3_iot_pruebas_token_super_seguro_1234567890")
DATABASE = "sensores"

devices = ["router_01", "router_02", "sensor_fabrica_A"]

with InfluxDBClient3(host=HOST, token=TOKEN, database=DATABASE) as client:
    print("Enviando telemetría continua a InfluxDB 3... (Ctrl+C para detener)")

    try:
        while True:
            for dev in devices:
                temp = round(random.uniform(20.0, 35.0), 2)
                lat = round(random.uniform(5.0, 45.0), 2)

                p = (Point("telemetria")
                     .tag("dispositivo", dev)
                     .field("temperatura", temp)
                     .field("latencia", lat))

                client.write(record=p)
                print(f"[{dev}] Ingestado -> Temp: {temp} °C | Latencia: {lat} ms")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nSimulación finalizada.")