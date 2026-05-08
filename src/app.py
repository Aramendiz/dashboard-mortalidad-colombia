import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings('ignore')

COLORWAY = ['#0f766e', '#2563eb', '#f59e0b', '#dc2626', '#7c3aed', '#0891b2']
PLOT_BG = '#ffffff'
TEXT_COLOR = '#122033'
MUTED_COLOR = '#64748b'

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
    title='Distribución de muertes por departamento',
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
    oceancolor='rgb(235, 246, 255)',
    showcountries=True,
    countrycolor='#94a3b8'
)
fig_mapa.update_traces(textposition='top center')
fig_mapa.update_layout(height=620)

# 2. GRÁFICO DE LÍNEAS
lineas_df = df.groupby('MES')['CONTEO'].sum().reset_index()
fig_lineas = px.line(lineas_df, x='MES', y='CONTEO', markers=True, 
                      title='Total de muertes por mes',
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
            title='Top 5 ciudades con más homicidios',
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
                    title='10 ciudades con menor mortalidad registrada',
                    hole=0.48,
                    color_discrete_sequence=COLORWAY)

# 5. TABLA - 10 principales causas de muerte
causas_df = df.groupby(['COD_MUERTE', 'CAUSA'])['CONTEO'].sum().nlargest(10).reset_index()
causas_df.columns = ['Código', 'Causa de Muerte', 'Total de Casos']
tabla_causas = dash_table.DataTable(
    columns=[{"name": col, "id": col} for col in causas_df.columns],
    data=causas_df.to_dict('records'), page_size=10,
    style_header={
        'backgroundColor': '#0f172a',
        'color': 'white',
        'fontWeight': '700',
        'border': '0',
        'fontFamily': 'Inter, system-ui, sans-serif',
        'padding': '14px'
    },
    style_cell={
        'textAlign': 'left',
        'fontSize': '14px',
        'fontFamily': 'Inter, system-ui, sans-serif',
        'border': '0',
        'borderBottom': '1px solid #e2e8f0',
        'padding': '13px 14px',
        'whiteSpace': 'normal',
        'height': 'auto',
        'color': TEXT_COLOR
    },
    style_data_conditional=[
        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'},
        {'if': {'column_id': 'Total de Casos'}, 'fontWeight': '700', 'color': '#0f766e'},
        {'if': {'column_id': 'Código'}, 'fontWeight': '700', 'color': '#334155'},
    ],
    style_table={'overflowX': 'auto', 'borderRadius': '12px', 'overflow': 'hidden'}
)

# 6. BARRAS APILADAS
apilado_df = df[df['DEPARTAMENTO'] != 'SIN DATOS'].groupby(['DEPARTAMENTO', 'SEXO'])['CONTEO'].sum().reset_index()
apilado_df['SEXO'] = apilado_df['SEXO'].map({1: 'Hombres', 2: 'Mujeres'}).fillna('Sin información')
# Tomar top 10 departamentos
top10_deptos = df[df['DEPARTAMENTO'] != 'SIN DATOS'].groupby('DEPARTAMENTO')['CONTEO'].sum().nlargest(10).index
apilado_df = apilado_df[apilado_df['DEPARTAMENTO'].isin(top10_deptos)]
fig_apilado = px.bar(apilado_df, x='DEPARTAMENTO', y='CONTEO', color='SEXO', 
                      barmode='stack', title='Muertes por sexo en los 10 departamentos con más casos',
                      labels={'CONTEO': 'Número de Muertes', 'SEXO': 'Sexo'},
                      color_discrete_map={'Hombres': '#2563eb', 'Mujeres': '#dc2626', 'Sin información': '#94a3b8'})

# 7. HISTOGRAMA
hist_df = df.groupby('CATEGORIA_EDAD')['CONTEO'].sum().reset_index()
orden_edades = ['Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia', 'Niñez', 
                'Adolescencia', 'Juventud', 'Adultez temprana', 'Adultez intermedia', 
                'Vejez', 'Longevidad / Centenarios', 'Edad desconocida', 'Sin información']
hist_df['CATEGORIA_EDAD'] = pd.Categorical(hist_df['CATEGORIA_EDAD'], categories=orden_edades, ordered=True)
hist_df = hist_df.sort_values('CATEGORIA_EDAD')
fig_histograma = px.bar(hist_df, x='CATEGORIA_EDAD', y='CONTEO', 
                         title='Distribución de muertes por ciclo de vida',
                         labels={'CONTEO': 'Número de Muertes'},
                         color='CONTEO',
                         color_continuous_scale='Teal')

total_muertes = len(df)
total_departamentos = df[df['DEPARTAMENTO'] != 'SIN DATOS']['DEPARTAMENTO'].nunique()
total_municipios = df[df['MUNICIPIO_NOMBRE'] != 'SIN DATOS']['MUNICIPIO_NOMBRE'].nunique()
principal_causa = causas_df.iloc[0]['Causa de Muerte']
principal_causa_total = causas_df.iloc[0]['Total de Casos']
mes_pico = lineas_df.loc[lineas_df['CONTEO'].idxmax()]
departamento_pico = mapa_df.iloc[0]

MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def format_number(value):
    return f"{int(value):,}".replace(",", ".")

def style_figure(fig, show_legend=True):
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        colorway=COLORWAY,
        font={'family': 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', 'color': TEXT_COLOR},
        title={'font': {'size': 18, 'color': TEXT_COLOR}, 'x': 0.02, 'xanchor': 'left'},
        margin={'l': 40, 'r': 24, 't': 66, 'b': 46},
        hoverlabel={'bgcolor': '#0f172a', 'font_size': 13, 'font_family': 'Inter, system-ui, sans-serif'},
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1} if show_legend else None
    )
    fig.update_xaxes(showgrid=False, linecolor='#e2e8f0', tickfont={'color': MUTED_COLOR}, title_font={'color': MUTED_COLOR})
    fig.update_yaxes(gridcolor='#edf2f7', zerolinecolor='#e2e8f0', tickfont={'color': MUTED_COLOR}, title_font={'color': MUTED_COLOR})
    return fig

for figure in [fig_lineas, fig_violentas, fig_pastel, fig_apilado, fig_histograma]:
    style_figure(figure)

style_figure(fig_mapa, show_legend=False)
fig_lineas.update_traces(line={'width': 4, 'color': '#0f766e'}, marker={'size': 9, 'color': '#0f766e'})
fig_violentas.update_layout(coloraxis_showscale=False)
fig_histograma.update_layout(coloraxis_showscale=False, xaxis_tickangle=-25)
fig_pastel.update_traces(textposition='inside', textinfo='percent+label', marker={'line': {'color': '#ffffff', 'width': 2}})

print("\n✅ Todos los gráficos creados exitosamente")

# ==================== 7. APLICACIÓN DASH ====================
print("\n🚀 Iniciando Dashboard...")

ASSETS_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder=ASSETS_PATH)
server = app.server

graph_config = {'displayModeBar': False, 'responsive': True}

def kpi_card(label, value, helper):
    return html.Div([
        html.P(label, className='kpi-label'),
        html.H3(value, className='kpi-value'),
        html.P(helper, className='kpi-helper')
    ], className='kpi-card')

def chart_card(title, description, figure=None, table=None, class_name=''):
    body = table if table is not None else dcc.Graph(figure=figure, config=graph_config, className='chart-graph')
    return html.Section([
        html.Div([
            html.H2(title),
            html.P(description)
        ], className='section-heading'),
        html.Div(body, className='visual-card')
    ], className=f'chart-section {class_name}')

app.layout = html.Div([
    html.Header([
        dbc.Container([
            html.Div([
                html.Span('Dashboard interactivo 2019', className='eyebrow'),
                html.H1('Mortalidad en Colombia'),
                html.P(
                    'Exploración visual de defunciones por territorio, tiempo, causa, sexo y ciclo de vida con datos del DANE y clasificación CIE-10.',
                    className='hero-copy'
                ),
                html.Div([
                    html.A('Repositorio GitHub', href='https://github.com/Aramendiz/dashboard-mortalidad-colombia', target='_blank', className='hero-link'),
                    html.A('Aplicación en Render', href='https://dashboard-mortalidad-colombia-5b7n.onrender.com', target='_blank', className='hero-link secondary')
                ], className='hero-actions')
            ], className='hero-content')
        ], fluid='xl')
    ], className='hero'),

    dbc.Container([
        dbc.Row([
            dbc.Col(kpi_card('Registros analizados', format_number(total_muertes), 'Defunciones consolidadas en la base 2019.'), lg=3, md=6),
            dbc.Col(kpi_card('Departamentos', format_number(total_departamentos), f"Mayor concentración: {departamento_pico['DEPARTAMENTO']}."), lg=3, md=6),
            dbc.Col(kpi_card('Municipios identificados', format_number(total_municipios), 'Cobertura territorial para lectura local.'), lg=3, md=6),
            dbc.Col(kpi_card('Mes con más casos', MESES.get(int(mes_pico['MES']), str(mes_pico['MES'])), f"{format_number(mes_pico['CONTEO'])} muertes registradas."), lg=3, md=6),
        ], className='kpi-grid'),

        chart_card(
            'Distribución territorial',
            'El tamaño de cada punto resume el volumen de muertes por departamento y permite ubicar rápidamente las zonas de mayor concentración.',
            figure=fig_mapa,
            class_name='featured'
        ),

        dbc.Row([
            dbc.Col(chart_card(
                'Comportamiento mensual',
                'La serie permite identificar variaciones durante el año y reconocer el mes de mayor registro.',
                figure=fig_lineas
            ), lg=6),
            dbc.Col(chart_card(
                'Ciudades con más homicidios',
                'Ranking construido con registros asociados a agresión por disparo de arma de fuego según códigos CIE-10 X95.',
                figure=fig_violentas
            ), lg=6),
        ], className='g-4'),

        dbc.Row([
            dbc.Col(chart_card(
                'Menor mortalidad municipal',
                'El gráfico resalta los municipios con menor número de defunciones registradas, filtrando valores mínimos para reducir ruido.',
                figure=fig_pastel
            ), lg=5),
            dbc.Col(chart_card(
                'Principales causas de muerte',
                f"La primera causa concentra {format_number(principal_causa_total)} casos. La tabla ordena los códigos y diagnósticos de mayor frecuencia.",
                table=tabla_causas
            ), lg=7),
        ], className='g-4'),

        chart_card(
            'Diferencias por sexo y departamento',
            'La comparación apilada muestra cómo se distribuyen las defunciones de hombres y mujeres en los departamentos con más casos.',
            figure=fig_apilado
        ),

        chart_card(
            'Mortalidad por ciclo de vida',
            'Las categorías de edad se agrupan según la tabla de referencia del DANE para reconocer los grupos con mayor vulnerabilidad.',
            figure=fig_histograma
        ),

        html.Footer([
            html.Strong('Fuente: '),
            html.Span('DANE - Estadísticas Vitales 2019. Clasificación de causas con códigos CIE-10.'),
            html.Span(f" Principal causa: {principal_causa}.", className='footer-note')
        ], className='site-footer')
    ], fluid='xl', className='main-content')
], className='app-shell')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print("\n" + "="*60)
    print(f"🌐 Dashboard: http://127.0.0.1:{port}")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
