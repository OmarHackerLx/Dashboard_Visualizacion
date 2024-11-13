import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os
import folium
from folium.plugins import HeatMap

# Definir la ruta del archivo Parquet
file_path = 'DatosParquet_reducido.parquet'  # Cambiado a ruta relativa

# Configuración de estilo
st.set_page_config(page_title="Dashboard de Puntajes y Estratos", layout="wide")
st.title('Dashboard de Puntajes y Estratos por Departamento')

# Verificar si el archivo Parquet existe
if os.path.exists(file_path):
    # Cargar el archivo Parquet
    df = pd.read_parquet(file_path)

    # Filtrar los datos eliminando valores nulos en 'ESTU_DEPTO_RESIDE'
    df_filtrado = df.dropna(subset=['ESTU_DEPTO_RESIDE'])

    # Crear un diccionario para mapear los valores de estratos a números
    estrato_mapping = {
        "Sin Estrato": None,
        "Estrato 1": 1,
        "Estrato 2": 2,
        "Estrato 3": 3,
        "Estrato 4": 4,
        "Estrato 5": 5,
        "Estrato 6": 6
    }

    # Reemplazar los valores de la columna 'FAMI_ESTRATOVIVIENDA' por valores numéricos
    df_filtrado['FAMI_ESTRATOVIVIENDA'] = df_filtrado['FAMI_ESTRATOVIVIENDA'].map(estrato_mapping)

    # Sidebar: Selección de puntaje y departamentos
    st.sidebar.header('Filtros del Dashboard')
    puntajes_columnas = ['PUNT_LECTURA_CRITICA', 'PUNT_MATEMATICAS', 'PUNT_C_NATURALES', 
                         'PUNT_SOCIALES_CIUDADANAS', 'PUNT_INGLES', 'PUNT_GLOBAL']
    selected_puntaje = st.sidebar.radio('Selecciona el puntaje a visualizar:', puntajes_columnas)

    # Agrupaciones y filtrado
    df_agrupado_puntajes = df.groupby('ESTU_DEPTO_RESIDE')[puntajes_columnas].mean().reset_index()
    df_agrupado_estrato = df_filtrado.dropna(subset=['FAMI_ESTRATOVIVIENDA']).groupby('ESTU_DEPTO_RESIDE')['FAMI_ESTRATOVIVIENDA'].mean().reset_index()
    departamentos = df_agrupado_puntajes['ESTU_DEPTO_RESIDE'].unique()
    selected_departamentos = st.sidebar.multiselect('Selecciona los departamentos:', options=departamentos, default=departamentos)

    df_filtrado_puntaje = df_agrupado_puntajes[df_agrupado_puntajes['ESTU_DEPTO_RESIDE'].isin(selected_departamentos)]
    df_filtrado_estrato = df_agrupado_estrato[df_agrupado_estrato['ESTU_DEPTO_RESIDE'].isin(selected_departamentos)]

    # Dashboard: Gráficos organizados en columnas
    col1, col2 = st.columns(2)

    # Gráfico de puntajes (ejes X e Y invertidos)
    with col1:
        st.subheader(f'Media de {selected_puntaje} por Departamento')
        if not df_filtrado_puntaje.empty:
            plt.figure(figsize=(12, 6))
            df_filtrado_puntaje = df_filtrado_puntaje.sort_values(by=selected_puntaje)
            bar_plot = sns.barplot(data=df_filtrado_puntaje, y='ESTU_DEPTO_RESIDE', x=selected_puntaje, palette='viridis')
            plt.title(f'Media del {selected_puntaje} por Departamento', fontsize=16)
            plt.ylabel('Departamento', fontsize=14)
            plt.xlabel(f'Media de {selected_puntaje}', fontsize=14)
            plt.xticks(rotation=0)
            for p in bar_plot.patches:
                bar_plot.annotate(f'{p.get_width():.1f}', (p.get_width(), p.get_y() + p.get_height() / 2.), ha='center', va='center', fontsize=8, color='black')
            st.pyplot(plt)
            plt.close()
        else:
            st.warning("No hay departamentos seleccionados para mostrar el gráfico de puntajes.")

    # Gráfico de estratos (ejes X e Y invertidos)
    with col2:
        st.subheader('Media de FAMI_ESTRATOVIVIENDA por Departamento')
        if not df_filtrado_estrato.empty:
            plt.figure(figsize=(12, 6))
            df_filtrado_estrato = df_filtrado_estrato.sort_values(by='FAMI_ESTRATOVIVIENDA')
            bar_plot_estrato = sns.barplot(data=df_filtrado_estrato, y='ESTU_DEPTO_RESIDE', x='FAMI_ESTRATOVIVIENDA', palette='coolwarm')
            plt.title('Media del Estrato de Vivienda por Departamento', fontsize=16)
            plt.ylabel('Departamento', fontsize=14)
            plt.xlabel('Media del Estrato de Vivienda', fontsize=14)
            plt.xticks(rotation=0)
            for p in bar_plot_estrato.patches:
                bar_plot_estrato.annotate(f'{p.get_width():.1f}', (p.get_width(), p.get_y() + p.get_height() / 2.), ha='center', va='center', fontsize=8, color='black')
            st.pyplot(plt)
            plt.close()
        else:
            st.warning("No hay datos disponibles para los departamentos seleccionados en el gráfico de estratos.")

    # Fila completa para gráfico de burbujas
    st.subheader(f'Relación entre {selected_puntaje}, Estrato y Departamento')
    if not df_filtrado_puntaje.empty and not df_filtrado_estrato.empty:
        df_combined = pd.merge(df_filtrado_puntaje, df_filtrado_estrato, on='ESTU_DEPTO_RESIDE')
        plt.figure(figsize=(14, 8))
        scatter_plot = sns.scatterplot(
            data=df_combined, 
            y='ESTU_DEPTO_RESIDE', 
            x=selected_puntaje, 
            size='FAMI_ESTRATOVIVIENDA', 
            sizes=(20, 200), 
            hue='FAMI_ESTRATOVIVIENDA', 
            palette='coolwarm', 
            legend="brief"
        )
        plt.title(f'Relación entre {selected_puntaje}, Estrato de Vivienda y Departamento', fontsize=16)
        plt.ylabel('Departamento', fontsize=14)
        plt.xlabel(f'Media de {selected_puntaje}', fontsize=14)
        plt.xticks(rotation=0)
        st.pyplot(plt)
        plt.close()
    else:
        st.warning("No hay datos suficientes para mostrar el gráfico de relación entre puntaje, estrato y departamento.")

    # Agregar el mapa interactivo de folium
    st.subheader("Mapa Interactivo de Puntajes por Departamento")

    # Diccionario de coordenadas de departamentos
    departamentos_coords = {
        "Amazonas": [-3.4653, -70.6513],
        "Antioquia": [6.4971, -75.3604],
        "Atlántico": [10.4218, -74.2116],
        "Bogotá": [4.6097, -74.0817],
        "Bolívar": [10.3910, -75.4794],
        "Boyacá": [5.5545, -73.3626],
        "Caldas": [5.0621, -75.5386],
        "Caquetá": [1.6111, -75.6167],
        "Casanare": [5.8590, -72.5225],
        "Cauca": [2.4967, -76.6052],
        "Cesar": [10.4630, -74.2792],
        "Chocó": [5.6915, -77.2035],
        "Córdoba": [8.7494, -75.8810],
        "Cundinamarca": [4.3457, -74.4582],
        "Guainía": [3.8750, -67.6699],
        "Guaviare": [3.0492, -71.5956],
        "Huila": [2.9166, -75.3703],
        "La Guajira": [11.5515, -71.7168],
        "Magdalena": [10.4775, -74.2199],
        "Meta": [4.0926, -73.7033],
        "Nariño": [1.2095, -77.2684],
        "Norte de Santander": [7.9305, -72.5071],
        "Putumayo": [1.3754, -76.6141],
        "Quindío": [4.5352, -75.6814],
        "Risaralda": [5.2637, -75.6042],
        "San Andrés y Providencia": [12.5800, -81.7117],
        "Santander": [7.6775, -73.1072],
        "Sucre": [9.2911, -75.4028],
        "Tolima": [4.0914, -75.2096],
        "Valle del Cauca": [3.4680, -76.5305],
        "Vaupés": [0.7405, -70.4971],
        "Vichada": [4.8673, -69.1814]
    }

    # Crear el mapa de folium centrado en Colombia
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)

    # Agregar puntos al mapa
    for depto in selected_departamentos:
        if depto in departamentos_coords:
            lat, lon = departamentos_coords[depto]
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
                popup=f'{depto}: {df_filtrado_puntaje[df_filtrado_puntaje["ESTU_DEPTO_RESIDE"] == depto][selected_puntaje].mean():.2f}'
            ).add_to(m)

    # Mostrar el mapa
    st.subheader("Mapa de Puntajes por Departamento")
    folium_static(m)

else:
    st.error('El archivo Parquet no fue encontrado en la ruta especificada.')
