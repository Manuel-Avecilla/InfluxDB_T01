# InfluxDB & Grafana - Monitoreo de Sensores (T01)

Este proyecto proporciona un entorno containerizado con **InfluxDB v3** y **Grafana** para la recolección, simulación y visualización de datos de sensores en tiempo real.

## Requisitos Previos

Asegúrate de contar con las siguientes herramientas instaladas en tu sistema:

* [Docker](https://www.docker.com/) y Docker Compose
* [Python 3.8+](https://www.python.org/)

## Inicio Rápido con Docker

### Levantar los Servicios

Ejecuta el siguiente comando para iniciar los contenedores de InfluxDB y Grafana en segundo plano:

```bash
docker compose up -d
```

### Acceso a Grafana

Una vez levantados los servicios, puedes acceder a la interfaz de Grafana a través de tu navegador:

* **Grafana Dashboard:** http://localhost:3000
* **Usuario:** admin
* **Contraseña:** admin

### Detener los Servicios

Para detener los contenedores y eliminar los volúmenes persistentes asociados:

```bash
docker compose down -v
```

## Configuración del Entorno Python

Para ejecutar los scripts de simulación, sigue estos pasos para configurar tu entorno virtual de Python:

```bash
# 1. Crear el entorno virtual
python3 -m venv venv

# 2. Activar el entorno virtual
source venv/bin/activate

# 3. Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución del Simulador

Con el entorno virtual activado, ejecuta el script de simulación de datos:

```bash
python simulador.py --backfill 10
```

> **Nota:** Para detener la ejecución del script en cualquier momento, presiona `Ctrl + C`.

## Configuración de Triggers en InfluxDB

Para registrar y configurar el *trigger* de downsampling (reducción de frecuencia a 5 minutos) en InfluxDB, ejecuta:

```bash
docker compose exec influxdb influxdb3 create trigger \
  --database sensores \
  --token apiv3_iot_pruebas_token_super_seguro_1234567890 \
  --path downsample_5m.py \
  --trigger-spec "every:1m" \
  downsample_5m
```