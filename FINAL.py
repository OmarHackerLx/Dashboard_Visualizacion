import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os
import folium
from streamlit_folium import folium_static

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

    # Mapa con Folium
    st.subheader('Mapa Interactivo de los Departamentos')
    df_folium = pd.DataFrame({
        'departamento': ['ANTIOQUIA', 'ATLÁNTICO', 'BOGOTÁ, D.C.', 'BOLÍVAR'],
        'lat': [6.702032125, 10.67700953, 4.316107698, 8.079796863],
        'lon': [-75.50455704, -74.96521949, -74.1810727, -74.23514814],
        'valor': [50, 60, 70, 40]
    })
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=6)
    min_value = df_folium['valor'].min()
    max_value = df_folium['valor'].max()
    color_scale = folium.LinearColormap(['blue', 'green', 'yellow', 'orange', 'red'], vmin=min_value, vmax=max_value)

    for i, row in df_folium.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"{row['departamento']}: {row['valor']}",
            icon=folium.Icon(color=color_scale(row['valor']), icon_color=color_scale(row['valor']), icon='info-sign')
        ).add_to(m)

    color_scale.add_to(m)
    folium_static(m)

else:
    st.error('El archivo Parquet no fue encontrado en la ruta especificada.')
