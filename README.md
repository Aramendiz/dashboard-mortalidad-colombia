# Dashboard de Mortalidad en Colombia - 2019

## Introducción
Este proyecto presenta un dashboard interactivo desarrollado con Dash y Plotly para analizar los patrones de mortalidad en Colombia durante el año 2019. La aplicación permite explorar visualmente la distribución geográfica, temporal, etaria y por causa de las defunciones registradas por el DANE.

## Objetivo
Identificar patrones demográficos y regionales de mortalidad en Colombia mediante visualizaciones interactivas que faciliten la interpretación de los datos y apoyen la toma de decisiones en salud pública.

## Estructura del proyecto

  ```text
  dashboard-mortalidad-colombia/
  ├── src/
  │   └── app.py            # Aplicación principal Dash
  ├── data/                 # Archivos de datos fuente
  ├── assets/               # Estilos CSS personalizados e imágenes
  ├── requirements.txt      # Dependencias del proyecto
  ├── render.yaml           # Configuración para despliegue en Render
  └── README.md             # Documentación del proyecto
  ```

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

### 🚀 Para desplegar en Render

1. **Sube todo** a un repositorio de GitHub.
2. **Crea una cuenta** en render.com.
3. **Haz clic** en "New +" → "Blueprint".
4. **Conecta** tu repositorio.
5. **Render leerá** render.yaml y desplegará automáticamente.
6. **Recibirás** una URL pública como: https://dashboard-mortalidad-colombia-5b7n.onrender.com

### Visualizaciones y resultados

### Mapa de mortalidad por departamento

Descripción: Un mapa de burbujas donde el tamaño de cada círculo representa el volumen total de defunciones por departamento.

<div align="center">
  <img src="./assets/img/mapa.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: Se identifica una concentración crítica en el triángulo andino (Antioquia, Valle del Cauca y Bogotá D.C.). Los departamentos de la periferia (Amazonía y Orinoquía) muestran burbujas significativamente menores, lo cual está correlacionado con la densidad poblacional del país.

### Gráfico de líneas por mes

Descripción: Gráfico de líneas que muestra la evolución de las defunciones mes a mes durante el año 2019.

<div align="center">
  <img src="./assets/img/grafico_lineas.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: El gráfico revela una caída drástica en el registro de muertes durante febrero (llegando al punto más bajo cerca de los 18k), seguida de una tendencia al alza que culmina en un pico máximo en diciembre (superando las 21.5k defunciones).

### Top 5 ciudades más violentas

Descripción: Ranking de las 5 ciudades con mayor número de registros bajo el código CIE-10 X95 (Agresión con disparo de arma de fuego).

<div align="center">
  <img src="./assets/img/grafico_barras.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: Santiago de Cali lidera esta estadística con 971 casos, seguida por Bogotá D.C. con 601. Este gráfico permite identificar geográficamente los focos de violencia externa en el país.

### Ciudades con menor mortalidad

Descripción: Gráfico de tipo donut que resalta los 10 municipios colombianos con el menor número de defunciones registradas en 2019.

<div align="center">
  <img src="./assets/img/grafico_circular.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: La distribución es notablemente equitativa entre estos municipios (cada uno con un 10% del total de este subgrupo), incluyendo localidades como Berbeo, Campohermoso y Chalán. Estos valores mínimos permiten identificar zonas con baja densidad poblacional o posibles casos de éxito en factores protectores de salud, una vez filtrado el ruido estadístico de la base de datos general.

### Tabla de causas de muerte

Descripción: Tabla detallada con los códigos CIE-10, diagnósticos y frecuencias absolutas.

<div align="center">
  <img src="./assets/img/tabla.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: El Infarto agudo del miocardio (I219) es, por un margen amplio, la principal causa de muerte en Colombia con 35,088 casos, superando casi por cinco veces a la segunda causa (EPOC).

### Barras apiladas por sexo y departamento

Descripción: Barras apiladas que comparan el volumen de defunciones entre hombres (azul) y mujeres (rojo) en los departamentos más afectados.

<div align="center">
  <img src="./assets/img/grafico_barras_apiladas.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: En todos los departamentos principales, la mortalidad masculina es superior a la femenina. En Bogotá D.C. y Antioquia, esta brecha es más pronunciada, lo que sugiere una mayor exposición de los hombres a riesgos de salud o factores externos.

### Histograma por ciclo de vida

Descripción: Distribución de frecuencias basada en las categorías de edad estandarizadas por el DANE.

<div align="center">
  <img src="./assets/img/histograma.png" alt="Dashboard de Mortalidad" width="600">
</div>

Hallazgo: El grupo de la Vejez concentra el mayor volumen de mortalidad (superando los 110k casos), lo cual es biológicamente esperado. Sin embargo, resalta un repunte en la Adultez Intermedia y una cifra no despreciable en Mortalidad Neonatal, puntos clave para políticas de prevención temprana.

### Software utilizado
 ``` text
  Python 3.11
  Dash 2.14
  Plotly 5.18
  Pandas 2.1
  Bootstrap 5
  Gunicorn (servidor de producción)
  ```

### Autores
  ```text
  Jairo Teófilo Araméndiz Pinzón
  Luz Aida Blandon Caicedo
  Fabio Gomez Estepa
  ```