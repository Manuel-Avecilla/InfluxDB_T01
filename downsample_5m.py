"""
Plugin programado (Processing Engine de InfluxDB 3) - Downsampling a 5 minutos.

Se ejecuta cada minuto (trigger every:1m sobre la database "sensores"):
  1. Lee trafico_raw de la database "sensores".
  2. Calcula la media de traffic_in, traffic_out y latency por router en
     ventanas de 5 minutos.
  3. Escribe el resultado en la database "trafico_5m" (tabla trafico_5m).

Notas:
  - LineBuilder ya está disponible dentro del Processing Engine (no se importa).
  - La consulta empieza en el límite de una ventana de 5 min, así nunca se
    calcula una ventana "cortada" a medias.
  - Escribir el mismo device + timestamp otra vez sobrescribe el punto, así que
    la ejecución cada minuto actualiza la ventana actual sin duplicar datos.
"""

SOURCE_TABLE = "trafico_raw"
TARGET_DB = "trafico_5m"
TARGET_TABLE = "trafico_5m"

SQL = f"""
SELECT date_bin(INTERVAL '5 minutes', time) AS ventana,
       device,
       AVG(traffic_in)  AS traffic_in,
       AVG(traffic_out) AS traffic_out,
       AVG(latency)     AS latency
FROM {SOURCE_TABLE}
WHERE time >= date_bin(INTERVAL '5 minutes', now() - INTERVAL '5 minutes')
GROUP BY ventana, device
ORDER BY ventana, device
"""

FIELDS = ("traffic_in", "traffic_out", "latency")


def process_scheduled_call(influxdb3_local, call_time, args=None):
    rows = influxdb3_local.query(SQL)

    if not rows:
        influxdb3_local.warn("downsample_5m: sin datos en trafico_raw para la ventana")
        return

    escritos = 0
    for row in rows:
        line = LineBuilder(TARGET_TABLE).tag("device", row["device"])  # noqa: F821
        tiene_campos = False
        for campo in FIELDS:
            valor = row.get(campo)
            if valor is not None:
                line.float64_field(campo, float(valor))
                tiene_campos = True
        if not tiene_campos:
            continue
        line.time_ns(int(row["ventana"]))
        influxdb3_local.write_to_db(TARGET_DB, line)
        escritos += 1

    influxdb3_local.info(f"downsample_5m: {escritos} puntos escritos en {TARGET_DB}.{TARGET_TABLE}")