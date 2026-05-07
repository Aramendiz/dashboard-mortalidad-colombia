import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("CARGANDO DATOS")
print("="*60)

# ==================== 1. CARGAR DEFUNCIONES ====================
df_def = pd.read_excel('data/defunciones2019.xlsx')
print(f"✓ Defunciones: {len(df_def):,} registros")

# ==================== 2. CARGAR DIVIPOLA ====================
# Crear diccionario de códigos a nombres de municipios
df_div = pd.read_excel('data/divipola.xlsx')

# Identificar columnas correctas
cod_col = None
nombre_col = None
depto_col = None

for col in df_div.columns:
    col_upper = str(col).upper()
    if 'COD_DANE' in col_upper or 'CÓDIGO' in col_upper:
        cod_col = col
    if 'MUNICIPIO' in col_upper or 'NOMBRE' in col_upper:
        nombre_col = col
    if 'DEPARTAMENTO' in col_upper:
        depto_col = col

# Si no encuentra, usar índices
if cod_col is None:
    cod_col = df_div.columns[0]
if nombre_col is None:
    nombre_col = df_div.columns[1]
if depto_col is None:
    depto_col = df_div.columns[2]

print(f"✓ Divipola: usando código={cod_col}, municipio={nombre_col}, depto={depto_col}")

# Crear diccionario de mapeo
df_div['COD_STR'] = df_div[cod_col].astype(str).str.zfill(5)
df_div['MUNICIPIO_NOMBRE'] = df_div[nombre_col].astype(str).str.upper()
df_div['DEPARTAMENTO'] = df_div[depto_col].astype(str).str.upper()

# Diccionario para mapear códigos a nombres
mapa_municipios = dict(zip(df_div['COD_STR'], df_div['MUNICIPIO_NOMBRE']))
mapa_departamentos = dict(zip(df_div['COD_STR'], df_div['DEPARTAMENTO']))

# ==================== 3. NORMALIZAR Y APLICAR MAPEO ====================
# Convertir COD_DANE a string de 5 dígitos
df_def['COD_DANE_STR'] = df_def['COD_DANE'].astype(str).str.zfill(5)

# Mapear nombres de municipios y departamentos
df_def['MUNICIPIO_NOMBRE'] = df_def['COD_DANE_STR'].map(mapa_municipios)
df_def['DEPARTAMENTO'] = df_def['COD_DANE_STR'].map(mapa_departamentos)

# Para los que no tienen match, intentar con COD_MUNICIPIO
sin_match = df_def['MUNICIPIO_NOMBRE'].isna()
if sin_match.sum() > 0:
    print(f"  Intentando con COD_MUNICIPIO para {sin_match.sum():,} registros...")
    df_def['COD_MPIO_3DIGITOS'] = df_def['COD_MUNICIPIO'].astype(str).str.zfill(3)
    
    # Crear diccionario con últimos 3 dígitos
    df_div['COD_MPIO_3D'] = df_div['COD_STR'].str[-3:]
    mapa_municipios_3d = dict(zip(df_div['COD_MPIO_3D'], df_div['MUNICIPIO_NOMBRE']))
    mapa_departamentos_3d = dict(zip(df_div['COD_MPIO_3D'], df_div['DEPARTAMENTO']))
    
    # Actualizar solo los que no tenían match
    mask = df_def['MUNICIPIO_NOMBRE'].isna()
    df_def.loc[mask, 'MUNICIPIO_NOMBRE'] = df_def.loc[mask, 'COD_MPIO_3DIGITOS'].map(mapa_municipios_3d)
    df_def.loc[mask, 'DEPARTAMENTO'] = df_def.loc[mask, 'COD_MPIO_3DIGITOS'].map(mapa_departamentos_3d)

# Limpiar nombres
df_def['MUNICIPIO_NOMBRE'] = df_def['MUNICIPIO_NOMBRE'].fillna('SIN DATOS')
df_def['DEPARTAMENTO'] = df_def['DEPARTAMENTO'].fillna('SIN DATOS')

matches = (df_def['MUNICIPIO_NOMBRE'] != 'SIN DATOS').sum()
print(f"✓ Registros con municipio identificado: {matches:,} de {len(df_def):,} ({matches/len(df_def)*100:.1f}%)")

# ==================== 4. CARGAR CÓDIGOS CIE-10 ====================
df_cie10 = pd.read_excel('data/cie10_codes.xlsx', sheet_name='Final', header=8)
print(f"✓ CIE-10: {len(df_cie10)} registros")

# Unir con CIE-10
df = df_def.merge(
    df_cie10[['Código de la CIE-10 cuatro caracteres', 'Descripcion  de códigos mortalidad a cuatro caracteres']],
    left_on='COD_MUERTE',
    right_on='Código de la CIE-10 cuatro caracteres',
    how='left'
)
df.rename(columns={'Descripcion  de códigos mortalidad a cuatro caracteres': 'CAUSA'}, inplace=True)
df['CAUSA'] = df['CAUSA'].fillna('No especificada')
df['CONTEO'] = 1

# ==================== 5. MAPEAR GRUPOS DE EDAD ====================
def mapear_edad(codigo):
    if pd.isna(codigo):
        return 'Sin información'
    if 0 <= codigo <= 4:
        return 'Mortalidad neonatal'
    if 5 <= codigo <= 6:
        return 'Mortalidad infantil'
    if 7 <= codigo <= 8:
        return 'Primera infancia'
    if 9 <= codigo <= 10:
        return 'Niñez'
    if codigo == 11:
        return 'Adolescencia'
    if 12 <= codigo <= 13:
        return 'Juventud'
    if 14 <= codigo <= 16:
        return 'Adultez temprana'
    if 17 <= codigo <= 19:
        return 'Adultez intermedia'
    if 20 <= codigo <= 24:
        return 'Vejez'
    if 25 <= codigo <= 28:
        return 'Longevidad / Centenarios'
    return 'Edad desconocida'

df['CATEGORIA_EDAD'] = df['GRUPO_EDAD1'].apply(mapear_edad)

print(f"\n✅ Datos procesados correctamente")
print(f"📊 Registros totales: {len(df):,}")

# Mostrar top 5 departamentos
top_deps = df[df['DEPARTAMENTO'] != 'SIN DATOS'].groupby('DEPARTAMENTO')['CONTEO'].sum().nlargest(5)
print("\n📊 Top 5 departamentos con más muertes:")
for depto, total in top_deps.items():
    print(f"  {depto}: {total:,}")

# Mostrar códigos de homicidios encontrados
codigos_homicidio = ['X95', 'X99', 'X93', 'X94', 'X91', 'X92', 'X96', 'X97', 'X98']
homicidios_encontrados = df[df['COD_MUERTE'].isin(codigos_homicidio)]['COD_MUERTE'].unique()
print(f"\n📊 Códigos de homicidio encontrados: {list(homicidios_encontrados)}")
print(f"📊 Total homicidios: {len(df[df['COD_MUERTE'].isin(codigos_homicidio)]):,}")

# ==================== 6. CREAR GRÁFICOS ====================
print("\n📈 Creando visualizaciones...")

# 1. MAPA - Usar solo departamentos con datos
mapa_df = df[df['DEPARTAMENTO'] != 'SIN DATOS'].groupby('DEPARTAMENTO')['CONTEO'].sum().reset_index(name='TOTAL')
mapa_df = mapa_df.sort_values('TOTAL', ascending=False)

# Coordenadas de departamentos
coords = {
    'AMAZONAS': (-2.5, -71.5), 'ANTIOQUIA': (6.5, -75.5), 'ARAUCA': (6.5, -71.0),
    'ATLANTICO': (10.8, -75.0), 'BOGOTÁ D.C.': (4.6, -74.1), 'BOGOTÁ': (4.6, -74.1),
    'BOLÍVAR': (9.0, -74.5), 'BOYACÁ': (5.5, -73.5), 'CALDAS': (5.2, -75.5),
    'CAQUETÁ': (1.5, -74.5), 'CASANARE': (5.5, -71.5), 'CAUCA': (2.5, -76.5),
    'CESAR': (9.3, -73.5), 'CHOCÓ': (6.0, -76.5), 'CÓRDOBA': (8.5, -75.5),
    'CUNDINAMARCA': (5.0, -74.0), 'GUAINÍA': (3.0, -68.0), 'GUAVIARE': (2.5, -70.0),
    'HUILA': (2.5, -75.5), 'LA GUAJIRA': (11.5, -72.5), 'MAGDALENA': (10.5, -74.5),
    'META': (3.5, -73.5), 'NARIÑO': (1.5, -77.5), 'NORTE DE SANTANDER': (7.9, -72.5),
    'PUTUMAYO': (1.0, -76.0), 'QUINDÍO': (4.5, -75.7), 'RISARALDA': (5.0, -75.8),
    'SAN ANDRÉS': (12.5, -81.7), 'SANTANDER': (7.0, -73.5), 'SUCRE': (9.0, -75.5),
    'TOLIMA': (4.5, -75.5), 'VALLE DEL CAUCA': (3.5, -76.5), 'VAUPÉS': (1.0, -70.0),
    'VICHADA': (5.5, -68.5),
}

mapa_df['LAT'] = mapa_df['DEPARTAMENTO'].apply(lambda x: coords.get(x, (4.5, -74.0))[0])
mapa_df['LON'] = mapa_df['DEPARTAMENTO'].apply(lambda x: coords.get(x, (4.5, -74.0))[1])

fig_mapa = px.scatter_geo(
    mapa_df, lat='LAT', lon='LON', size='TOTAL', 
    hover_name='DEPARTAMENTO', text='DEPARTAMENTO',
    title='📌 Distribución de Muertes por Departamento (2019)',
    size_max=80, scope='south america',
    labels={'TOTAL': 'Número de Muertes'},
    center={'lat': 4.5, 'lon': -74.0}
)
# Enfocar solo Colombia
fig_mapa.update_geos(
    lataxis_range=[-4.5, 12.5],
    lonaxis_range=[-79.0, -66.0],
    resolution=110,
    showcoastlines=True,
    coastlinecolor='black',
    showland=True,
    landcolor='rgb(243, 243, 243)',
    showocean=True,
    oceancolor='rgb(230, 242, 255)',
    showcountries=True,
    countrycolor='black'
)
fig_mapa.update_traces(textposition='top center')
fig_mapa.update_layout(height=600, width=1200)

# 2. GRÁFICO DE LÍNEAS
lineas_df = df.groupby('MES')['CONTEO'].sum().reset_index()
fig_lineas = px.line(lineas_df, x='MES', y='CONTEO', markers=True, 
                      title='Total de Muertes por Mes',
                      labels={'MES': 'Mes', 'CONTEO': 'Número de Muertes'})

# 3. TOP 5 CIUDADES MÁS VIOLENTAS (homicidios - CÓDIGOS X95 Y SIMILARES)
# Según CIE-10: X95  son agresiones (homicidios), X95 = Agresión con disparo de arma de fuego
codigos_homicidio = ['X950', 'X951', 'X952', 'X953', 'X954', 'X955', 'X956', 'X957', 'X958', 'X959']
homicidios_df = df[df['COD_MUERTE'].isin(codigos_homicidio)]

print(f"\n🔍 Depuración gráfico violentas:")
print(f"  Total registros con códigos de homicidio: {len(homicidios_df):,}")
print(f"  Códigos encontrados: {homicidios_df['COD_MUERTE'].unique().tolist()}")

if len(homicidios_df) > 0:
    # Filtrar solo los que tienen municipio identificado
    homicidios_con_municipio = homicidios_df[homicidios_df['MUNICIPIO_NOMBRE'] != 'SIN DATOS']
    print(f"  Registros con municipio identificado: {len(homicidios_con_municipio):,}")
    
    if len(homicidios_con_municipio) > 0:
        # Agrupar por municipio y sumar
        violentas = homicidios_con_municipio.groupby('MUNICIPIO_NOMBRE')['CONTEO'].sum().reset_index()
        violentas.columns = ['MUNICIPIO', 'HOMICIDIOS']
        violentas = violentas.sort_values('HOMICIDIOS', ascending=False).head(5)
        
        print(f"  Top 5 ciudades violentas encontradas:")
        for i, row in violentas.iterrows():
            print(f"    - {row['MUNICIPIO']}: {row['HOMICIDIOS']:,} homicidios")
        
        fig_violentas = px.bar(
            violentas, 
            x='MUNICIPIO', 
            y='HOMICIDIOS', 
            title='⚠️ Top 5 Ciudades Más Violentas (Homicidios)',
            text='HOMICIDIOS',
            color='HOMICIDIOS', 
            color_continuous_scale='Reds'
        )
        fig_violentas.update_traces(textposition='outside')
        fig_violentas.update_layout(
            xaxis_title="Ciudad",
            yaxis_title="Número de Homicidios",
            height=500
        )
    else:
        fig_violentas = px.scatter(title="No se pudieron identificar municipios para los homicidios")
else:
    # Si no hay homicidios con esos códigos, mostrar los códigos más comunes como alternativa
    print(f"\n  ⚠️ No se encontraron homicidios con códigos específicos.")
    print(f"  Códigos más comunes en general: {df['COD_MUERTE'].value_counts().head(10).to_dict()}")
    fig_violentas = px.scatter(
        title="No hay datos de homicidios (códigos X95-X99) en los registros.\n"
              "Los códigos más comunes son: " + ", ".join(df['COD_MUERTE'].value_counts().head(5).index.tolist())
    )
    fig_violentas.update_layout(height=400)

# 4. GRÁFICO CIRCULAR - 10 ciudades con menor mortalidad
mort_ciudad = df[df['MUNICIPIO_NOMBRE'] != 'SIN DATOS'].groupby('MUNICIPIO_NOMBRE')['CONTEO'].sum()
# Filtrar municipios con al menos 10 muertes para evitar ruido
mort_ciudad = mort_ciudad[mort_ciudad >= 10]
lowest = mort_ciudad.nsmallest(10).reset_index()
lowest.columns = ['MUNICIPIO', 'MUERTES']
fig_pastel = px.pie(lowest, names='MUNICIPIO', values='MUERTES', 
                    title='🍩 10 Ciudades con Menor Índice de Mortalidad')

# 5. TABLA - 10 principales causas de muerte
causas_df = df.groupby(['COD_MUERTE', 'CAUSA'])['CONTEO'].sum().nlargest(10).reset_index()
causas_df.columns = ['Código', 'Causa de Muerte', 'Total de Casos']
tabla_causas = dash_table.DataTable(
    columns=[{"name": col, "id": col} for col in causas_df.columns],
    data=causas_df.to_dict('records'), page_size=10,
    style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
    style_cell={'textAlign': 'left', 'fontSize': '14px'},
    style_table={'overflowX': 'auto'}
)

# 6. BARRAS APILADAS
apilado_df = df[df['DEPARTAMENTO'] != 'SIN DATOS'].groupby(['DEPARTAMENTO', 'SEXO'])['CONTEO'].sum().reset_index()
# Tomar top 10 departamentos
top10_deptos = df[df['DEPARTAMENTO'] != 'SIN DATOS'].groupby('DEPARTAMENTO')['CONTEO'].sum().nlargest(10).index
apilado_df = apilado_df[apilado_df['DEPARTAMENTO'].isin(top10_deptos)]
fig_apilado = px.bar(apilado_df, x='DEPARTAMENTO', y='CONTEO', color='SEXO', 
                      barmode='stack', title='👥 Comparación de Muertes por Sexo (Top 10 Departamentos)',
                      labels={'CONTEO': 'Número de Muertes', 'SEXO': 'Sexo'})

# 7. HISTOGRAMA
hist_df = df.groupby('CATEGORIA_EDAD')['CONTEO'].sum().reset_index()
orden_edades = ['Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia', 'Niñez', 
                'Adolescencia', 'Juventud', 'Adultez temprana', 'Adultez intermedia', 
                'Vejez', 'Longevidad / Centenarios', 'Edad desconocida', 'Sin información']
hist_df['CATEGORIA_EDAD'] = pd.Categorical(hist_df['CATEGORIA_EDAD'], categories=orden_edades, ordered=True)
hist_df = hist_df.sort_values('CATEGORIA_EDAD')
fig_histograma = px.bar(hist_df, x='CATEGORIA_EDAD', y='CONTEO', 
                         title='📊 Distribución de Muertes por Ciclo de Vida',
                         labels={'CONTEO': 'Número de Muertes'})

print("\n✅ Todos los gráficos creados exitosamente")

# ==================== 7. APLICACIÓN DASH ====================
print("\n🚀 Iniciando Dashboard...")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("📊 Análisis de Mortalidad en Colombia - 2019", className="text-center my-4"),
    html.Hr(),
    
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_mapa), width=12)]),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_lineas), width=6), dbc.Col(dcc.Graph(figure=fig_violentas), width=6)]),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_pastel), width=5), dbc.Col(tabla_causas, width=7)]),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_apilado), width=12)]),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_histograma), width=12)]),
    
    html.Hr(),
    html.Footer(html.P("Fuente: DANE - Estadísticas Vitales 2019 | Códigos CIE-10", 
                       className="text-center text-muted"))
], fluid=True)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 Dashboard: http://127.0.0.1:8050")
    print("="*60)
    app.run(debug=True)