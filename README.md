# InfluxDB_T01

Para levantar los contenedores de InfluxDB y Grafana, ejecutar el siguiente comando:
```bash
docker compose up -d 
```

Para detener los contenedores y eliminar volúmenes persistentes, ejecutar el siguiente comando:
```bash
# Detener los contenedores y eliminar volúmenes persistentes
docker compose down -v
```

URL de acceso a Grafana: [http://localhost:3000](http://localhost:3000)

Para preparar el entorno de ejecución de los scripts:
```bash

# Crear el entorno virtual
python3 -m venv venv
```

```bash
# Activar el entorno virtual
source venv/bin/activate
```

```bash
# Actualizar el gestor de paquetes e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Despues de crear y activar el entorno virtual, podemos ejecutar los scripts:
```bash
# Ejecutar el script
python simulador.py
```
```bash
# Ejecutar el script
python generador_sensores_temp.py
```
ctrl + c para detener la ejecución de los scripts.
