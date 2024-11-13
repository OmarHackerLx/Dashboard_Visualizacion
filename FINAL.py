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
    df_departamentos = pd.DataFrame({
        'departamento': ['ANTIOQUIA', 'ATLÁNTICO', 'BOGOTÁ, D.C.', 'BOLÍVAR', 'BOYACÁ', 'CALDAS', 'CAQUETÁ', 'CAUCA', 'CESAR',
                         'CÓRDOBA', 'CUNDINAMARCA', 'CHOCÓ', 'HUILA', 'LA GUAJIRA', 'MAGDALENA', 'META', 'NARIÑO', 'NORTE DE SANTANDER',
                         'QUINDÍO', 'RISARALDA', 'SANTANDER', 'SUCRE', 'TOLIMA', 'VALLE DEL CAUCA', 'ARAUCA', 'CASANARE', 'PUTUMAYO',
                         'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA', 'AMAZONAS', 'GUAINÍA', 'GUAVIARE', 'VAUPÉS', 'VICHADA'],
        'lat': [6.702032125, 10.67700953, 4.316107698, 8.079796863, 5.891672889, 5.280139978, 0.798556195, 2.396833887,
                9.53665993, 8.358549754, 4.771120716, 5.397581542, 2.570143029, 11.47687008, 10.24738355, 3.345562732,
                1.571094987, 8.09513751, 4.455241567, 5.240757239, 6.693633184, 9.064941448, 4.03477252, 3.569858693,
                6.569577215, 5.404064237, 0.3673031, 12.54311512, -1.54622768, 2.727842865, 1.924531973, 0.636634748],
        'lon': [-75.70126393, -74.99083812, -74.08314411, -75.56359151, -73.3098892, -75.65086642, -75.88069712,
                -76.61891398, -73.71933693, -73.98701565, -74.31816735, -76.59874151, -76.36552059, -71.94553734,
                -74.18925577, -75.49758114, -73.88174804, -77.13996262, -72.9946198, -74.01301523, -74.10234115,
                -74.01650449, -75.08012079, -73.30850847, -76.60725149, -75.76277267, -70.62495717, -74.22350052,
                -75.24183943, -73.49826767, -72.49750711, -69.5161272, -69.92474764]
    })

    # Filtrar departamentos según la selección
    df_departamentos_filtrados = df_departamentos[df_departamentos['departamento'].isin(selected_departamentos)]

    # Crear el mapa
    m = folium.Map(location=[4.570868, -74.297333], zoom_start=5, control_scale=True)

    for i in df_departamentos_filtrados.iterrows():
        folium.Marker([i[1]['lat'], i[1]['lon']], popup=f"<b>{i[1]['departamento']}</b>").add_to(m)

    folium_static(m)

else:
    st.error("El archivo no existe o no se pudo cargar.")
