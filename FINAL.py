import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from math import pi
from sklearn.preprocessing import MinMaxScaler

# Cargar el DataFrame
df = pd.read_parquet('DatosParquet.parquet')

# Preprocesamiento de los datos
df_radar = df[['ESTU_DEPTO_RESIDE', 'FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
               'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS', 'PUNT_GLOBAL']]

# Limpieza de datos
df_radar['FAMI_ESTRATOVIVIENDA'] = df_radar['FAMI_ESTRATOVIVIENDA'].replace({'Sin Estrato': None}).str.replace('Estrato ', '', regex=False).astype(float)
diccionario_educacion = {
    'Postgrado': 13, 'Educación profesional completa': 12, 'Educación profesional incompleta': 11,
    'Técnica o tecnológica completa': 10, 'Secundaria (Bachillerato) completa': 9, 'Primaria completa': 8,
    'Técnica o tecnológica incompleta': 7, 'Secundaria (Bachillerato) incompleta': 6, 'Primaria incompleta': 5,
    'Ninguno': 4, 'No Aplica': 3, 'No sabe': 2, None: 1
}
df_radar['FAMI_EDUCACIONPADRE'] = df_radar['FAMI_EDUCACIONPADRE'].replace(diccionario_educacion)
df_radar['FAMI_EDUCACIONMADRE'] = df_radar['FAMI_EDUCACIONMADRE'].replace(diccionario_educacion)
df_radar['FAMI_TIENEINTERNET'] = df_radar['FAMI_TIENEINTERNET'].replace({'Sí': 1, 'No': 0, 'Si': 1}).astype(float)
df_radar['FAMI_TIENECOMPUTADOR'] = df_radar['FAMI_TIENECOMPUTADOR'].replace({'Sí': 1, 'No': 0, 'Si': 1}).astype(float)
df_radar['FAMI_NUMLIBROS'] = df_radar['FAMI_NUMLIBROS'].replace({'MÁS DE 100 LIBROS': 5, '26 A 100 LIBROS': 4, 
                                                                  '11 A 25 LIBROS': 3, '0 A 10 LIBROS': 2, None: 1}).astype(float)

# Filtrar los datos para el mapa
df_mapa = df[['ESTU_DEPTO_RESIDE', 'PUNT_GLOBAL']]
df_mapa = df_mapa[~df_mapa['ESTU_DEPTO_RESIDE'].isin(['EXTRANJERO', None])]
promedios = df_mapa.groupby('ESTU_DEPTO_RESIDE')['PUNT_GLOBAL'].mean().reset_index()
promedios.rename(columns={'PUNT_GLOBAL': 'PROMEDIO_PUNT_GLOBAL'}, inplace=True)

# Añadir las coordenadas de los departamentos
coordenadas = {
    'ANTIOQUIA': (6.702032125, -75.50455704), 'ATLANTICO': (10.67700953, -74.96521949), 'BOGOTÁ': (4.316107698, -74.1810727),
    'BOLIVAR': (8.079796863, -74.23514814), 'BOYACA': (5.891672889, -72.62788054), 'CALDAS': (5.280139978, -75.27498304),
    'CAQUETA': (0.798556195, -73.95946756), 'CAUCA': (2.396833887, -76.82423283), 'CESAR': (9.53665993, -73.51783154),
    'CORDOBA': (8.358549754, -75.79200872), 'CUNDINAMARCA': (4.771120716, -74.43111092), 'CHOCO': (5.397581542, -76.942811),
    'HUILA': (2.570143029, -75.58434836), 'LA GUAJIRA': (11.47687008, -72.42951072), 'MAGDALENA': (10.24738355, -74.26175733),
    'META': (3.345562732, -72.95645988), 'NARIÑO': (1.571094987, -77.87020496), 'NORTE SANTANDER': (8.09513751, -72.88188297),
    'QUINDIO': (4.455241567, -75.68962853), 'RISARALDA': (5.240757239, -76.00244469), 'SANTANDER': (6.693633184, -73.48600894),
    'SUCRE': (9.064941448, -75.10981755), 'TOLIMA': (4.03477252, -75.2558271), 'VALLE': (3.569858693, -76.62850427),
    'ARAUCA': (6.569577215, -70.96732394), 'CASANARE': (5.404064237, -71.60188073), 'PUTUMAYO': (0.3673031, -75.51406183),
    'SAN ANDRES': (12.54311512, -81.71762382), 'AMAZONAS': (-1.54622768, -71.50212858), 'GUAINIA': (2.727842865, -68.81661272),
    'GUAVIARE': (1.924531973, -72.12859569), 'VAUPES': (0.64624561, -70.56140566), 'VICHADA': (4.713557125, -69.41400011)
}

promedios['LATITUD'] = promedios['ESTU_DEPTO_RESIDE'].map(lambda x: coordenadas[x][0] if x in coordenadas else None)
promedios['LONGITUD'] = promedios['ESTU_DEPTO_RESIDE'].map(lambda x: coordenadas[x][1] if x in coordenadas else None)

# Normalizar los datos para el radar
df_radar_normalizado = df_radar.copy()
scaler = MinMaxScaler()
df_radar_normalizado[['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE',
                      'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']] = scaler.fit_transform(
    df_radar[['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE',
              'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']])

# Streamlit - Filtros
st.title("Análisis Interactivo de Datos")
departamento_seleccionado = st.selectbox('Selecciona un Departamento', df['ESTU_DEPTO_RESIDE'].unique())
filtro_estrato = st.slider('Filtro de Estrato', 1, 6, (1, 6))

# Filtrar los datos según la selección del usuario
df_filtrado = df_radar[df_radar['ESTU_DEPTO_RESIDE'] == departamento_seleccionado]
df_filtrado = df_filtrado[df_filtrado['FAMI_ESTRATOVIVIENDA'].between(filtro_estrato[0], filtro_estrato[1])]

# Gráfico de radar
def radar_plot():
    bogota_data = df_radar_normalizado[df_radar_normalizado['ESTU_DEPTO_RESIDE'] == 'BOGOTÁ']
    choco_data = df_radar_normalizado[df_radar_normalizado['ESTU_DEPTO_RESIDE'] == 'CHOCO']

    promedios_bogota = bogota_data[['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE',
                                     'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']].mean().tolist()
    promedios_choco = choco_data[['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE',
                                   'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']].mean().tolist()

    etiquetas = ['Estrato de Vivienda', 'Nivel Educativo del Padre', 'Nivel Educativo de la Madre',
                 'Acceso a Internet', 'Disponibilidad de Computadora', 'Número de Libros del Hogar']

    # Crear gráfico de radar
    num_vars = len(etiquetas)
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
    ax.set_xticklabels(etiquetas, fontsize=10, color='black', fontweight='bold')
    ax.set_title(f'Comparación Normalizada - {departamento_seleccionado}', fontsize=12, color='black', fontweight='bold', y=1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=10, frameon=True, shadow=True, fancybox=True)

    st.pyplot(fig)

# Gráfico de barras
def bar_plot():
    df_agrupado = df.groupby('ESTU_DEPTO_RESIDE')['PUNT_GLOBAL'].mean().reset_index()
    df_agrupado = df_agrupado[df_agrupado['ESTU_DEPTO_RESIDE'] == departamento_seleccionado]
    sns.set(style="whitegrid")
    plt.figure(figsize=(14, 8))
    sns.barplot(data=df_agrupado, y='ESTU_DEPTO_RESIDE', x='PUNT_GLOBAL', palette="muted")
    plt.title(f'Comparativa del Puntaje Global - {departamento_seleccionado}', fontsize=18, weight='bold', color='black')
    plt.xlabel('Media del Puntaje Global', fontsize=16, fontweight='bold')
    plt.ylabel('Departamento', fontsize=16, fontweight='bold')
    plt.tight_layout()

    st.pyplot(plt)

# Gráfico de burbuja
def bubble_plot():
    df_means = df.groupby('ESTU_DEPTO_RESIDE').agg(
        media_puntaje=('PUNT_GLOBAL', 'mean'),
        media_estrato=('FAMI_ESTRATOVIVIENDA', 'mean')
    ).reset_index()

    plt.figure(figsize=(16, 10))
    sns.scatterplot(data=df_means, x='media_estrato', y='media_puntaje', size='media_puntaje', hue='ESTU_DEPTO_RESIDE', palette='tab20')
    plt.title(f'Gráfico de Media de Estrato vs Media de Puntaje por Departamento', fontsize=20)
    plt.xlabel('Media de Estrato', fontsize=16)
    plt.ylabel('Media de Puntaje', fontsize=16)
    st.pyplot(plt)

# Mapa interactivo
def map_plot():
    mapa = folium.Map(location=[4.5709, -74.2973], zoom_start=5)
    for index, row in promedios.iterrows():
        folium.CircleMarker(
            location=[row['LATITUD'], row['LONGITUD']],
            radius=10,
            color='blue' if row['PROMEDIO_PUNT_GLOBAL'] < 2 else 'orange' if row['PROMEDIO_PUNT_GLOBAL'] < 3 else 'red',
            fill=True,
            fill_color='blue' if row['PROMEDIO_PUNT_GLOBAL'] < 2 else 'orange' if row['PROMEDIO_PUNT_GLOBAL'] < 3 else 'red',
            fill_opacity=0.7,
            popup=f"{row['ESTU_DEPTO_RESIDE']}: {row['PROMEDIO_PUNT_GLOBAL']}"
        ).add_to(mapa)

    st.write(mapa)

# Mostrar los gráficos
radar_plot()
bar_plot()
bubble_plot()
map_plot()
