# Dashboard de Mortalidad en Colombia - 2019

## Introducción
Este proyecto presenta un dashboard interactivo desarrollado con Dash y Plotly para analizar los patrones de mortalidad en Colombia durante el año 2019. La aplicación permite explorar visualmente la distribución geográfica, temporal, etaria y por causa de las defunciones registradas por el DANE.

## Objetivo
Identificar patrones demográficos y regionales de mortalidad en Colombia mediante visualizaciones interactivas que faciliten la interpretación de los datos y apoyen la toma de decisiones en salud pública.

## Estructura del proyecto
dashboard-mortalidad-colombia/
├── src/
│ └── app.py # Aplicación principal Dash
├── data/ # Archivos de datos fuente
├── assets/ # Estilos CSS personalizados
├── requirements.txt # Dependencias del proyecto
├── render.yaml # Configuración para despliegue en Render
└── README.md # Documentación del proyecto

text

## Requisitos
- Python 3.11 o superior
- Librerías: dash, plotly, pandas, openpyxl, gunicorn

## Instalación y ejecución local
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Aramendiz/dashboard-mortalidad-colombia.git
   cd dashboard-mortalidad-colombia
   ```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```bash
python src/app.py
```

5. Abrir el navegador en http://127.0.0.1:8050

### 📄Despliegue en Render

1. Subir el código a un repositorio de GitHub.
2. Crear una cuenta en render.com.
3. Seleccionar "New +" → "Blueprint" y conectar el repositorio.
4. Render detectará automáticamente el archivo render.yaml.
5. Hacer clic en "Deploy Blueprint".
6. La aplicación estará disponible en una URL similar a: https://dashboard-mortalidad-colombia.onrender.com

### Visualizaciones y resultados

### Mapa de mortalidad por departamento

El mapa muestra la distribución geográfica de las muertes. Se observa una mayor concentración en departamentos densamente poblados como Antioquia, Valle del Cauca y Cundinamarca.

### Gráfico de líneas por mes

Revela la variación estacional de las defunciones, con picos en meses específicos que podrían asociarse a fenómenos climáticos o epidemiológicos.

### Top 5 ciudades más violentas

Identifica las ciudades con mayor número de homicidios (código X95), destacando las principales urbes del país.

### Ciudades con menor mortalidad

Muestra las localidades con menor número de defunciones, útil para estudios de factores protectores.

### Tabla de causas de muerte

Lista las 10 causas más frecuentes, permitiendo identificar las principales amenazas para la salud pública.

### Barras apiladas por sexo y departamento

Compara la mortalidad entre hombres y mujeres en cada departamento, evidenciando diferencias significativas por género.

### Histograma por ciclo de vida

Distribuye las muertes según las categorías etarias definidas por el DANE, mostrando los grupos de mayor vulnerabilidad (vejez, adultez intermedia, mortalidad neonatal).

### Software utilizado

Python 3.11
Dash 2.14
Plotly 5.18
Pandas 2.1
Bootstrap 5
Gunicorn (servidor de producción)

### Autor

Jairo Teófilo Araméndiz Pinzón - Aplicaciones 1/Universidad La Salle]


### ▶️ Pasos para ejecutar

1. **Crea la estructura de carpetas** exactamente como se muestra arriba.
2. **Copia el código de `app.py`** en `src/app.py`.
3. **Copia el `requirements.txt`** y `render.yaml` en la raíz.
4. **Coloca tus 3 archivos Excel** dentro de la carpeta `data/`.
5. **Ejecuta**:
   ```bash
   pip install -r requirements.txt
   python src/app.py
   ```
6. **Abre** http://127.0.0.1:8050 en tu navegador

### 🚀 Para desplegar en Render

1. **Sube todo** a un repositorio de GitHub.
2. **Crea una cuenta** en render.com.
3. **Haz clic** en "New +" → "Blueprint".
4. **Conecta** tu repositorio.
5. **Render leerá** render.yaml y desplegará automáticamente.
6. **Recibirás** una URL pública como: https://dashboard-mortalidad-colombia.onrender.com