import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os
import folium
from folium import plugins
from streamlit_folium import folium_static
import matplotlib.colors as mcolors

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

    # Coordenadas de los departamentos
    coordenadas = {
        'departamento': [
            'ANTIOQUIA', 'ATLÁNTICO', 'BOGOTÁ, D.C.', 'BOLÍVAR', 'BOYACÁ', 'CALDAS', 'CAQUETÁ', 'CAUCA', 'CESAR',
            'CÓRDOBA', 'CUNDINAMARCA', 'CHOCÓ', 'HUILA', 'LA GUAJIRA', 'MAGDALENA', 'META', 'NARIÑO', 'NORTE DE SANTANDER',
            'QUINDÍO', 'RISARALDA', 'SANTANDER', 'SUCRE', 'TOLIMA', 'VALLE DEL CAUCA', 'ARAUCA', 'CASANARE', 'PUTUMAYO',
            'SAN ANDRÉS', 'AMAZONAS', 'GUAINÍA', 'GUAVIARE', 'VAUPÉS', 'VICHADA'
        ],
        'lat': [
            6.702032125, 10.67700953, 4.316107698, 8.079796863, 5.891672889, 5.280139978, 0.798556195, 2.396833887,
            9.53665993, 8.358549754, 4.771120716, 5.397581542, 2.570143029, 11.47687008, 10.24738355, 3.345562732,
            1.571094987, 8.09513751, 4.455241567, 5.240757239, 6.693633184, 9.064941448, 4.03477252, 3.569858693,
            6.569577215, 5.404064237, 0.3673031, 12.54311512, -1.54622768, 2.727842865, 1.924531973, 0.64624561, 4.713557125
        ],
        'lon': [
            -75.50455704, -74.96521949, -74.1810727, -74.23514814, -72.62788054, -75.27498304, -73.95946756, -76.82423283,
            -73.51783154, -75.79200872, -74.43111092, -76.942811, -75.58434836, -72.42951072, -74.26175733, -72.95645988,
            -77.87020496, -72.88188297, -75.68962853, -76.00244469, -73.48600894, -75.10981755, -75.2558271, -76.62850427,
            -70.96732394, -71.60188073, -75.51406183, -81.71762382, -71.50212858, -68.81661272, -72.12859569, -70.56140566,
            -69.41400011
        ]
    }

    # Crear DataFrame de coordenadas
    df_coordenadas = pd.DataFrame(coordenadas)

    # Unir el DataFrame de puntajes con las coordenadas
    df_filtrado_puntaje = pd.merge(df_filtrado_puntaje, df_coordenadas, left_on='ESTU_DEPTO_RESIDE', right_on='departamento')

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
            st.warning("No hay departamentos seleccionados para mostrar el gráfico de estratos.")

    # Mapa con Folium
    st.subheader('Mapa Interactivo de los Departamentos')

    # Mapa base
    m = folium.Map(location=[4.570868, -74.297333], zoom_start=5)

    # Definir la escala de colores con valores mínimos y máximos del puntaje
    min_value = df_filtrado_puntaje[selected_puntaje].min()
    max_value = df_filtrado_puntaje[selected_puntaje].max()
    color_scale = folium.LinearColormap(['blue', 'green', 'yellow', 'orange', 'red'], vmin=min_value, vmax=max_value)

    # Agregar los marcadores con colores basados en el puntaje
    for _, row in df_filtrado_puntaje.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"{row['departamento']}: {selected_puntaje} = {row[selected_puntaje]:.1f}",
            icon=folium.Icon(color=color_scale(row[selected_puntaje]), icon_color="white", icon='info-sign')
        ).add_to(m)

    # Agregar la leyenda del mapa
    color_scale.add_to(m)

    # Mostrar el mapa
    folium_static(m)

else:
    st.error("No se encontró el archivo de datos. Asegúrate de que esté en el directorio correcto.")
