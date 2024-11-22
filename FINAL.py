import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from math import pi
from io import BytesIO

# Cargar datos
@st.cache
def cargar_datos():
    df = pd.read_parquet('DatosParquet.parquet')
    return df

# Cargar y procesar datos
df = cargar_datos()

# Procesamiento de datos para el radar
def procesar_datos_radar(df):
    df_radar = df[['ESTU_DEPTO_RESIDE', 'FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
                   'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS', 'PUNT_GLOBAL']]
    
    # Reemplazo de valores y conversión
    df_radar['FAMI_ESTRATOVIVIENDA'] = df_radar['FAMI_ESTRATOVIVIENDA'].replace({'Sin Estrato': None}).str.replace('Estrato ', '', regex=False).astype(float)
    
    orden_educacion = [
        ('Postgrado', 13), ('Educación profesional completa', 12), ('Educación profesional incompleta', 11),
        ('Técnica o tecnológica completa', 10), ('Secundaria (Bachillerato) completa', 9),
        ('Primaria completa', 8), ('Técnica o tecnológica incompleta', 7), ('Secundaria (Bachillerato) incompleta', 6),
        ('Primaria incompleta', 5), ('Ninguno', 4), ('No Aplica', 3), ('No sabe', 2), (None, 1)
    ]
    diccionario_educacion = dict(orden_educacion)
    
    df_radar['FAMI_EDUCACIONPADRE'] = df_radar['FAMI_EDUCACIONPADRE'].replace(diccionario_educacion)
    df_radar['FAMI_EDUCACIONMADRE'] = df_radar['FAMI_EDUCACIONMADRE'].replace(diccionario_educacion)

    df_radar['FAMI_TIENEINTERNET'] = df_radar['FAMI_TIENEINTERNET'].replace({'Sí': 1, 'No': 0, 'Si': 1}).astype(float)
    df_radar['FAMI_TIENECOMPUTADOR'] = df_radar['FAMI_TIENECOMPUTADOR'].replace({'Sí': 1, 'No': 0, 'Si': 1}).astype(float)

    orden_libros = [
        ('MÁS DE 100 LIBROS', 5), ('26 A 100 LIBROS', 4), ('11 A 25 LIBROS', 3), 
        ('0 A 10 LIBROS', 2), (None, 1)
    ]
    diccionario_libros = dict(orden_libros)

    df_radar['FAMI_NUMLIBROS'] = df_radar['FAMI_NUMLIBROS'].replace(diccionario_libros).astype(float)
    
    return df_radar

# Función para mostrar el gráfico radar
def mostrar_radar(df_radar):
    df_radar_normalizado = df_radar.copy()
    columnas_a_normalizar = ['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
                             'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']

    for columna in columnas_a_normalizar:
        min_val = df_radar_normalizado[columna].min()
        max_val = df_radar_normalizado[columna].max()
        df_radar_normalizado[columna] = (df_radar_normalizado[columna] - min_val) / (max_val - min_val)
    
    bogota_data_normalizado = df_radar_normalizado[df_radar_normalizado['ESTU_DEPTO_RESIDE'] == 'BOGOTÁ']
    choco_data_normalizado = df_radar_normalizado[df_radar_normalizado['ESTU_DEPTO_RESIDE'] == 'CHOCO']
    
    promedios_bogota_normalizados = bogota_data_normalizado[columnas_a_normalizar].mean()
    promedios_choco_normalizados = choco_data_normalizado[columnas_a_normalizar].mean()
    
    nuevas_etiquetas = [
        'Estrato de Vivienda', 'Nivel Educativo del Padre', 'Nivel Educativo de la Madre', 
        'Acceso a Internet', 'Disponibilidad de Computadora', 'Número de Libros del Hogar'
    ]
    
    promedios_bogota = promedios_bogota_normalizados.tolist()
    promedios_choco = promedios_choco_normalizados.tolist()

    num_vars = len(nuevas_etiquetas)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    promedios_bogota += promedios_bogota[:1]
    promedios_choco += promedios_choco[:1]

    fig, ax = plt.subplots(figsize=(7, 7), dpi=100, subplot_kw=dict(polar=True))

    ax.plot(angles, promedios_bogota, color='green', linewidth=2, linestyle='solid', label='Bogotá')
    ax.fill(angles, promedios_bogota, color='green', alpha=0.25)

    ax.plot(angles, promedios_choco, color='red', linewidth=2, linestyle='solid', label='Chocó')
    ax.fill(angles, promedios_choco, color='red', alpha=0.25)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(nuevas_etiquetas, fontsize=10, color='black', fontweight='bold')

    ax.set_title('Comparación Normalizada entre Bogotá y Chocó', fontsize=12, color='black', fontweight='bold', y=1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=10, frameon=True, shadow=True, fancybox=True)

    plt.tight_layout()
    st.pyplot(fig)

# Función para mostrar gráfico de barras
def mostrar_barras(df):
    puntaje_columnas = ['PUNT_GLOBAL']

    df_agrupado = df.groupby('ESTU_DEPTO_RESIDE')[puntaje_columnas].mean().reset_index()

    df_agrupado = df_agrupado[df_agrupado['ESTU_DEPTO_RESIDE'].isin(['BOGOTÁ', 'CHOCO'])]
    df_agrupado['ESTU_DEPTO_RESIDE'] = df_agrupado['ESTU_DEPTO_RESIDE'].replace({'BOGOTÁ': 'Bogotá', 'CHOCO': 'Chocó'})

    sns.set(style="whitegrid")
    plt.figure(figsize=(14, 8))

    df_agrupado = df_agrupado.sort_values(by='PUNT_GLOBAL', ascending=False)

    custom_palette = {'Bogotá': '#006400', 'Chocó': '#8B0000'}

    bar_plot = sns.barplot(data=df_agrupado, y='ESTU_DEPTO_RESIDE', x='PUNT_GLOBAL', palette=custom_palette)

    plt.title('Comparativa del Puntaje Global por Departamento', fontsize=18, weight='bold', color='black')
    plt.xlabel('Media del Puntaje Global', fontsize=16, fontweight='bold')
    plt.ylabel('Departamento', fontsize=16, fontweight='bold')

    bar_plot.set_yticklabels(bar_plot.get_yticklabels(), fontsize=16, fontweight='bold', color='black')

    for p in bar_plot.patches:
        value = round(p.get_width())
        bar_plot.annotate(f'{value}', 
                          (p.get_width() / 2, p.get_y() + p.get_height() / 2.), 
                          ha='center', va='center', fontsize=16, fontweight='bold', color='white')

    plt.tight_layout()
    st.pyplot(fig)

# Función para mostrar el mapa
def mostrar_mapa(promedios):
    mapa = folium.Map(location=[4.5709, -74.2973], zoom_start=5, control_scale=True)

    min_puntaje = promedios['PROMEDIO_PUNT_GLOBAL'].min()
    max_puntaje = promedios['PROMEDIO_PUNT_GLOBAL'].max()

    def get_color(puntaje):
        rango = max_puntaje - min_puntaje
        if puntaje >= min_puntaje + 0.67 * rango:
            return 'red'
        elif puntaje >= min_puntaje + 0.33 * rango:
            return 'orange'
        else:
            return 'blue'

    for index, row in promedios.iterrows():
        color = get_color(row['PROMEDIO_PUNT_GLOBAL'])

        folium.CircleMarker(
            location=[row['LATITUD'], row['LONGITUD']],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"{row['DEPTO']} - Promedio Puntaje Global: {row['PROMEDIO_PUNT_GLOBAL']}",
        ).add_to(mapa)

    st.markdown('### Mapa de Puntajes por Departamento')
    st.components.v1.html(mapa._repr_html_(), height=600)

# Configuración de la aplicación
st.title('Análisis de Datos de Estudiantes')

# Mostrar gráficas
st.subheader('Gráfico Radar')
df_radar = procesar_datos_radar(df)
mostrar_radar(df_radar)

st.subheader('Gráfico de Barras del Puntaje Global')
mostrar_barras(df)

st.subheader('Mapa de Puntajes por Departamento')
promedios = df.groupby(['DEPTO', 'LATITUD', 'LONGITUD'])['PUNT_GLOBAL'].mean().reset_index()
mostrar_mapa(promedios)
