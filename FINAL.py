import pandas as pd
import folium
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os
from streamlit_folium import folium_static

# Definir la ruta del archivo Parquet
file_path = 'DatosParquet_reducido.parquet'

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

    # Actualizar df_folium con los valores correspondientes al puntaje seleccionado
    df_folium = pd.DataFrame({
        'departamento': df_filtrado_puntaje['ESTU_DEPTO_RESIDE'],
        'lat': [6.702032125, 10.67700953, 4.316107698, 8.079796863, 5.891672889, 5.280139978, 0.798556195, 2.396833887,
                9.53665993, 8.358549754, 4.771120716, 5.397581542, 2.570143029, 11.47687008, 10.24738355, 3.345562732,
                1.571094987, 8.09513751, 4.455241567, 5.240757239, 6.693633184, 9.064941448, 4.03477252, 3.569858693,
                6.569577215, 5.404064237, 0.3673031, 12.54311512, -1.54622768, 2.727842865, 1.924531973, 0.64624561, 4.713557125],  # Latitudes (ajustar si es necesario)
        'lon': [-75.50455704, -74.96521949, -74.1810727, -74.23514814, -72.62788054, -75.27498304, -73.95946756, -76.82423283,
                -73.51783154, -75.79200872, -74.43111092, -76.942811, -75.58434836, -72.42951072, -74.26175733, -72.95645988,
                -77.87020496, -72.88188297, -75.68962853, -76.00244469, -73.48600894, -75.10981755, -75.2558271, -76.62850427,
                -70.96732394, -71.60188073, -75.51406183, -81.71762382, -71.50212858, -68.81661272, -72.12859569, -70.56140566,
                -69.41400011],  # Longitudes (ajustar si es necesario)
        'valor': df_filtrado_puntaje[selected_puntaje]  # Asignar los valores del puntaje seleccionado
    })

    # Crear el mapa centrado en Colombia
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=6)

    # Definir una lista de colores que van de azul a rojo
    min_value = df_folium['valor'].min()
    max_value = df_folium['valor'].max()
    color_scale = folium.LinearColormap(['blue', 'green', 'yellow', 'orange', 'red'], vmin=min_value, vmax=max_value)

    # Agregar los departamentos al mapa con colores y valores en el popup
    for i, row in df_folium.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"{row['departamento']}: {row['valor']}",
            icon=folium.Icon(color=color_scale(row['valor']), icon_color=color_scale(row['valor']), icon='info-sign')
        ).add_to(m)

    # Agregar la leyenda del mapa
    color_scale.add_to(m)

    # Mostrar el mapa
    folium_static(m)

    # Mostrar el gráfico de barras de la media por departamento
    st.subheader(f'Media de {selected_puntaje} por Departamento')
    plt.figure(figsize=(10, 6))
    sns.barplot(x='ESTU_DEPTO_RESIDE', y=selected_puntaje, data=df_filtrado_puntaje, palette='coolwarm')
    plt.xticks(rotation=90)
    plt.title(f'Media de {selected_puntaje} por Departamento')
    plt.xlabel('Departamento')
    plt.ylabel(f'{selected_puntaje}')
    st.pyplot()

    # Mostrar el gráfico de estratos por departamento
    st.subheader('Promedio de Estrato por Departamento')
    plt.figure(figsize=(10, 6))
    sns.barplot(x='ESTU_DEPTO_RESIDE', y='FAMI_ESTRATOVIVIENDA', data=df_filtrado_estrato, palette='viridis')
    plt.xticks(rotation=90)
    plt.title('Promedio de Estrato por Departamento')
    plt.xlabel('Departamento')
    plt.ylabel('Estrato Promedio')
    st.pyplot()

else:
    st.error('El archivo Parquet no fue encontrado en la ruta especificada.')
