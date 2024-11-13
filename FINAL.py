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

    # Mapa de calor de puntajes por Departamento
    st.subheader(f'Mapa de Calor de {selected_puntaje} por Departamento')

    # Crear un DataFrame para el mapa
    df_map = df_filtrado_puntaje[['ESTU_DEPTO_RESIDE', selected_puntaje]]

    # Coordenadas aproximadas de los departamentos (latitud, longitud)
    departamento_coords = {
        'ANTIOQUIA': [6.702032125, -75.50455704], 'ATLÁNTICO': [10.67700953, -74.96521949], 'BOGOTÁ, D.C.': [4.316107698, -74.1810727],
        'BOLÍVAR': [8.079796863, -74.23514814], 'BOYACÁ': [5.891672889, -72.62788054], 'CALDAS': [5.280139978, -75.27498304],
        'CAQUETÁ': [0.798556195, -73.95946756], 'CAUCA': [2.396833887, -76.82423283], 'CESAR': [9.53665993, -73.51783154],
        'CÓRDOBA': [8.358549754, -75.79200872], 'CUNDINAMARCA': [4.771120716, -74.43111092], 'CHOCÓ': [5.397581542, -76.942811],
        # Añadir las coordenadas para el resto de departamentos...
    }

    # Crear el mapa centrado en Colombia
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=6)

    # Definir una lista de colores que van de azul a rojo
    min_value = df_map[selected_puntaje].min()
    max_value = df_map[selected_puntaje].max()
    color_scale = folium.LinearColormap(['blue', 'green', 'yellow', 'orange', 'red'], vmin=min_value, vmax=max_value)

    # Agregar los departamentos al mapa con colores según el puntaje
    for i, row in df_map.iterrows():
        if row['ESTU_DEPTO_RESIDE'] in departamento_coords:
            folium.Marker(
                location=departamento_coords[row['ESTU_DEPTO_RESIDE']],
                popup=f"{row['ESTU_DEPTO_RESIDE']}: {row[selected_puntaje]:.2f}",
                icon=folium.Icon(color=color_scale(row[selected_puntaje]), icon_color=color_scale(row[selected_puntaje]), icon='info-sign')
            ).add_to(m)

    # Agregar la leyenda del mapa
    color_scale.add_to(m)

    # Mostrar el mapa
    st.markdown("### Mapa de Calor de Puntajes por Departamento")
    st.write(m)

else:
    st.error('El archivo Parquet no fue encontrado en la ruta especificada.')
