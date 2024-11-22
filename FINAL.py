import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from math import pi

# Cargar el DataFrame
@st.cache
def cargar_dataframe():
    return pd.read_parquet('DatosParquet.parquet')

df = cargar_dataframe()

# Mostrar el DataFrame
st.title('Análisis de Datos')
st.write(df.head())

# Radar
st.header('Comparación Normalizada entre Bogotá y Chocó')
# Procesar los datos para el gráfico de radar
df_radar = df[['ESTU_DEPTO_RESIDE', 'FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
               'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS', 'PUNT_GLOBAL']]

# Normalización y procesamiento
columnas_a_normalizar = ['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
                         'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']

# Normalizar los datos
df_radar_normalizado = df_radar.copy()
for columna in columnas_a_normalizar:
    min_val = df_radar_normalizado[columna].min()
    max_val = df_radar_normalizado[columna].max()
    df_radar_normalizado[columna] = (df_radar_normalizado[columna] - min_val) / (max_val - min_val)

# Filtrar los datos para Bogotá y Chocó
bogota_data_normalizado = df_radar_normalizado[df_radar_normalizado['ESTU_DEPTO_RESIDE'] == 'BOGOTÁ']
choco_data_normalizado = df_radar_normalizado[df_radar_normalizado['ESTU_DEPTO_RESIDE'] == 'CHOCO']

# Promedios de Bogotá y Chocó
promedios_bogota_normalizados = bogota_data_normalizado[columnas_a_normalizar].mean()
promedios_choco_normalizados = choco_data_normalizado[columnas_a_normalizar].mean()

nuevas_etiquetas = ['Estrato de Vivienda', 'Nivel Educativo del Padre', 'Nivel Educativo de la Madre', 
                    'Acceso a Internet', 'Disponibilidad de Computadora', 'Número de Libros del Hogar']

# Crear gráfico de radar
promedios_bogota = promedios_bogota_normalizados.tolist()
promedios_choco = promedios_choco_normalizados.tolist()

# Número de categorías
num_vars = len(nuevas_etiquetas)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # Cerrar el gráfico

promedios_bogota += promedios_bogota[:1]
promedios_choco += promedios_choco[:1]

fig, ax = plt.subplots(figsize=(7, 7), dpi=100, subplot_kw=dict(polar=True))

# Crear gráfico de radar para Bogotá
ax.plot(angles, promedios_bogota, color='green', linewidth=2, linestyle='solid', label='Bogotá')
ax.fill(angles, promedios_bogota, color='green', alpha=0.25)

# Crear gráfico de radar para Chocó
ax.plot(angles, promedios_choco, color='red', linewidth=2, linestyle='solid', label='Chocó')
ax.fill(angles, promedios_choco, color='red', alpha=0.25)

# Añadir etiquetas
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(nuevas_etiquetas, fontsize=10, color='black', fontweight='bold')

ax.set_title('Comparación Normalizada entre Bogotá y Chocó', fontsize=12, color='black', fontweight='bold', y=1.1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=10, frameon=True, shadow=True, fancybox=True)

plt.tight_layout()

# Mostrar gráfico de radar
st.pyplot(fig)

# Mapa
st.header('Mapa de Puntajes Promedio por Departamento')

# Coordenadas de los departamentos
coordenadas = {
    'ANTIOQUIA': (6.702032125, -75.50455704),
    'ATLANTICO': (10.67700953, -74.96521949),
    'BOGOTÁ': (4.316107698, -74.1810727),
    # Añadir las demás coordenadas...
}

# Promedios por departamento
df_mapa = df[['ESTU_DEPTO_RESIDE', 'PUNT_GLOBAL']]
promedios = df_mapa.groupby('ESTU_DEPTO_RESIDE')['PUNT_GLOBAL'].mean().reset_index()
promedios.rename(columns={'PUNT_GLOBAL': 'PROMEDIO_PUNT_GLOBAL'}, inplace=True)

promedios['LATITUD'] = promedios['ESTU_DEPTO_RESIDE'].map(lambda x: coordenadas[x][0] if x in coordenadas else None)
promedios['LONGITUD'] = promedios['ESTU_DEPTO_RESIDE'].map(lambda x: coordenadas[x][1] if x in coordenadas else None)

# Crear mapa
mapa = folium.Map(location=[4.5709, -74.2973], zoom_start=5, control_scale=True)

# Función para asignar colores según puntaje
def get_color(puntaje):
    if puntaje >= promedios['PROMEDIO_PUNT_GLOBAL'].max() - 0.1:
        return 'red'
    elif puntaje >= promedios['PROMEDIO_PUNT_GLOBAL'].min() + 0.1:
        return 'orange'
    else:
        return 'blue'

# Añadir los puntos al mapa
for _, row in promedios.iterrows():
    folium.CircleMarker(
        location=[row['LATITUD'], row['LONGITUD']],
        radius=10,
        color=get_color(row['PROMEDIO_PUNT_GLOBAL']),
        fill=True,
        fill_color=get_color(row['PROMEDIO_PUNT_GLOBAL']),
        fill_opacity=0.6
    ).add_to(mapa)

# Mostrar mapa en Streamlit
st.write(mapa)
