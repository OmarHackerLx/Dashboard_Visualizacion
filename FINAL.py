import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from math import pi

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

    # Preparar datos para el gráfico radar
    columnas_radar = ['ESTU_DEPTO_RESIDE', 'FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
                      'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS', 'PUNT_GLOBAL']
    df_radar = df[columnas_radar]

    # Preprocesar los datos de las columnas de radar
    estrato_mapping_radar = {
        "Sin Estrato": None,
        "Estrato 1": 1,
        "Estrato 2": 2,
        "Estrato 3": 3,
        "Estrato 4": 4,
        "Estrato 5": 5,
        "Estrato 6": 6
    }
    df_radar['FAMI_ESTRATOVIVIENDA'] = df_radar['FAMI_ESTRATOVIVIENDA'].map(estrato_mapping_radar)

    # Diccionario de niveles de educación
    orden_educacion = [
        ('Postgrado', 13),
        ('Educación profesional completa', 12),
        ('Educación profesional incompleta', 11),
        ('Técnica o tecnológica completa', 10),
        ('Secundaria (Bachillerato) completa', 9),
        ('Primaria completa', 8),
        ('Técnica o tecnológica incompleta', 7),
        ('Secundaria (Bachillerato) incompleta', 6),
        ('Primaria incompleta', 5),
        ('Ninguno', 4),
        ('No Aplica', 3),
        ('No sabe', 2),
        (None, 1)
    ]
    diccionario_educacion = dict(orden_educacion)

    # Reemplazar educación
    df_radar['FAMI_EDUCACIONPADRE'] = df_radar['FAMI_EDUCACIONPADRE'].replace(diccionario_educacion)
    df_radar['FAMI_EDUCACIONMADRE'] = df_radar['FAMI_EDUCACIONMADRE'].replace(diccionario_educacion)

    # Convertir a numérico FAMI_TIENEINTERNET y FAMI_TIENECOMPUTADOR
    df_radar['FAMI_TIENEINTERNET'] = df_radar['FAMI_TIENEINTERNET'].apply(lambda x: 1 if x == 'Si' else 0)
    df_radar['FAMI_TIENECOMPUTADOR'] = df_radar['FAMI_TIENECOMPUTADOR'].apply(lambda x: 1 if x == 'Si' else 0)

    # Normalización de datos
    columnas_existentes = [col for col in df_radar.columns if col != 'ESTU_DEPTO_RESIDE']
    df_radar_normalizado = df_radar[["ESTU_DEPTO_RESIDE"] + columnas_existentes].copy()

    # Asegurar que las columnas sean numéricas y eliminar NaN
    for columna in columnas_existentes:
        if df_radar_normalizado[columna].dtype not in ['float64', 'int64']:
            df_radar_normalizado[columna] = pd.to_numeric(df_radar_normalizado[columna], errors='coerce')
    df_radar_normalizado = df_radar_normalizado.dropna(subset=columnas_existentes)

    # Normalizar las columnas
    for columna in columnas_existentes:
        min_val = df_radar_normalizado[columna].min()
        max_val = df_radar_normalizado[columna].max()
        if max_val != min_val:
            df_radar_normalizado[columna] = (df_radar_normalizado[columna] - min_val) / (max_val - min_val)
        else:
            df_radar_normalizado[columna] = 0

    # Código para mostrar gráfico radar
    st.subheader('Gráfico Radar de Puntajes y Características')
    if not df_radar_normalizado.empty:
        # Agregar aquí el código del gráfico radar que prefieras.
        st.write("Gráfico radar se debe agregar aquí.")
else:
    st.error("El archivo no existe. Por favor, verifica la ubicación del archivo Parquet.")
