import streamlit as st
import pandas as pd
import folium
from folium import plugins
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import seaborn as sns

# Asumiendo que tienes df_filtrado_puntaje que es el DataFrame filtrado
# Primero seleccionamos el departamento y la columna de puntaje
departamentos = df_filtrado_puntaje['ESTU_DEPTO_RESIDE'].unique()
selected_departamento = st.selectbox('Selecciona un departamento:', departamentos)

# Ahora seleccionamos el puntaje de la columna para la media por departamento
selected_puntaje = st.selectbox('Selecciona el puntaje a visualizar:', df_filtrado_puntaje.columns)

# Media de puntajes por departamento
media_por_departamento = df_filtrado_puntaje.groupby('ESTU_DEPTO_RESIDE')[selected_puntaje].mean().reset_index()

# Mostrar gráfico de la media por departamento
st.subheader(f"Media de {selected_puntaje} por Departamento")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=media_por_departamento, x='ESTU_DEPTO_RESIDE', y=selected_puntaje, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.pyplot(fig)

# Datos de latitudes y longitudes para los departamentos de Colombia
latitudes = [
    6.702032125, 10.67700953, 4.316107698, 8.079796863, 5.891672889, 5.280139978, 0.798556195, 2.396833887,
    9.53665993, 8.358549754, 4.771120716, 5.397581542, 2.570143029, 11.47687008, 10.24738355, 3.345562732,
    1.571094987, 8.09513751, 4.455241567, 5.240757239, 6.693633184, 9.064941448, 4.03477252, 3.569858693,
    6.569577215, 5.404064237, 0.3673031, 12.54311512, -1.54622768, 2.727842865, 1.924531973, 0.64624561, 4.713557125
]

longitudes = [
    -75.50455704, -74.96521949, -74.1810727, -74.23514814, -72.62788054, -75.27498304, -73.95946756, -76.82423283,
    -73.51783154, -75.79200872, -74.43111092, -76.942811, -75.58434836, -72.42951072, -74.26175733, -72.95645988,
    -77.87020496, -72.88188297, -75.68962853, -76.00244469, -73.48600894, -75.10981755, -75.2558271, -76.62850427,
    -70.96732394, -71.60188073, -75.51406183, -81.71762382, -71.50212858, -68.81661272, -72.12859569, -70.56140566,
    -69.41400011
]

# Filtrar los datos para el departamento seleccionado
df_departamento = df_filtrado_puntaje[df_filtrado_puntaje['ESTU_DEPTO_RESIDE'] == selected_departamento]

# Aseguramos que el número de departamentos seleccionados coincida con el número de latitudes y longitudes
if len(latitudes) == len(longitudes) == len(df_filtrado_puntaje):
    # Crear el DataFrame de folium
    df_folium = pd.DataFrame({
        'departamento': df_filtrado_puntaje['ESTU_DEPTO_RESIDE'],
        'lat': latitudes[:len(df_filtrado_puntaje)],  # Limitar la longitud de latitudes
        'lon': longitudes[:len(df_filtrado_puntaje)],  # Limitar la longitud de longitudes
        'valor': df_filtrado_puntaje[selected_puntaje]  # Asignar los valores del puntaje seleccionado
    })
else:
    st.error("El número de departamentos seleccionados no coincide con el número de latitudes y longitudes disponibles.")

# Crear mapa usando Folium
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

# Mostrar el mapa en Streamlit
folium_static(m)

# Crear HeatMap si el usuario lo solicita
if st.checkbox("Mostrar HeatMap"):
    heat_data = [[row['lat'], row['lon'], row['valor']] for i, row in df_folium.iterrows()]
    HeatMap(heat_data).add_to(m)
    folium_static(m)

# Los demás gráficos que ya tienes...
# Gráfico de dispersión
st.subheader(f"Gráfico de dispersión de {selected_puntaje}")
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df_filtrado_puntaje, x='ESTU_DEPTO_RESIDE', y=selected_puntaje, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.pyplot(fig)

# Histograma de puntajes
st.subheader(f"Histograma de {selected_puntaje}")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df_filtrado_puntaje[selected_puntaje], kde=True, ax=ax)
st.pyplot(fig)

# Boxplot de puntajes por departamento
st.subheader(f"Boxplot de {selected_puntaje} por Departamento")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_filtrado_puntaje, x='ESTU_DEPTO_RESIDE', y=selected_puntaje, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.pyplot(fig)

# Gráfico de correlación
st.subheader(f"Correlación entre variables")
correlation_matrix = df_filtrado_puntaje.corr()
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# Gráfico de distribución acumulativa
st.subheader(f"Distribución acumulativa de {selected_puntaje}")
fig, ax = plt.subplots(figsize=(10, 6))
sns.ecdfplot(df_filtrado_puntaje[selected_puntaje], ax=ax)
st.pyplot(fig)
