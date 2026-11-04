import os
import time
import random
from influxdb_client_3 import InfluxDBClient3, Point

# Configuración de conexión (InfluxDB 3 Core: sin organización, "database" en vez de "bucket")
HOST = "http://localhost:8181"
TOKEN = os.getenv("INFLUX_TOKEN", "apiv3_iot_pruebas_token_super_seguro_1234567890")
DATABASE = "sensores"

# Inicializar cliente
client = InfluxDBClient3(host=HOST, token=TOKEN, database=DATABASE)

print("🚀 Enviando datos de telemetría a InfluxDB 3 (Presiona Ctrl+C para detener)...")

try:
    while True:
        # Generar valores simulados
        temp = round(random.uniform(18.0, 35.0), 2)
        hum = round(random.uniform(40.0, 80.0), 2)

        # Construir punto de datos (Line Protocol)
        point = Point("clima") \
            .tag("ubicacion", "sevilla") \
            .field("temperatura", temp) \
            .field("humedad", hum)

        # Enviar a InfluxDB
        client.write(record=point)
        print(f"Enviado -> temperatura={temp}ºC, humedad={hum}%")

        time.sleep(2)  # Pausa de 2 segundos entre lecturas

except KeyboardInterrupt:
    print("\nSimulación finalizada.")
finally:
    client.close()