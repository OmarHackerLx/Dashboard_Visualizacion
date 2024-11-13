import folium
from folium.plugins import HeatMap
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Cargar el archivo Parquet
df_filtrado_puntaje = pd.read_parquet("ruta_a_tu_archivo.parquet")

# Lista de departamentos y sus coordenadas (latitud y longitud)
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
    "San Andrés y Providencia": [12.5847, -81.7111],
    "Santander": [7.6899, -73.9352],
    "Sucre": [9.3130, -75.3640],
    "Tolima": [4.0985, -75.6057],
    "Valle del Cauca": [3.4372, -76.5223],
    "Vaupés": [0.9467, -70.6398],
    "Vichada": [5.1495, -67.1978]
}

# Columna de puntajes a utilizar
selected_puntaje = "Puntaje_promedio"  # Ajusta este nombre de columna si es necesario

# Crear el mapa centrado en Colombia
colombia_map = folium.Map(location=[4.5709, -74.2973], zoom_start=6)

# Agregar HeatMap con los datos de los departamentos y sus puntajes
heat_data = []
for depto, coords in departamentos_coords.items():
    if depto in df_filtrado_puntaje['ESTU_DEPTO_RESIDE'].values:
        promedio_puntaje = df_filtrado_puntaje[df_filtrado_puntaje['ESTU_DEPTO_RESIDE'] == depto][selected_puntaje].values[0]
        heat_data.append([coords[0], coords[1], promedio_puntaje])

# Crear el HeatMap
HeatMap(heat_data).add_to(colombia_map)

# Mostrar el mapa en Streamlit
map_html = colombia_map._repr_html_()  # Este método obtiene el código HTML del mapa
st.markdown(map_html, unsafe_allow_html=True)

# Gráfico de puntajes por departamento
st.subheader("Puntajes Promedio por Departamento")

# Gráfico de barras
puntajes_por_departamento = df_filtrado_puntaje.groupby("ESTU_DEPTO_RESIDE")[selected_puntaje].mean().reset_index()
plt.figure(figsize=(10, 6))
sns.barplot(x="ESTU_DEPTO_RESIDE", y=selected_puntaje, data=puntajes_por_departamento, palette="viridis")
plt.xticks(rotation=90)
plt.title("Puntajes Promedio por Departamento")
plt.xlabel("Departamento")
plt.ylabel("Puntaje Promedio")
st.pyplot(plt)

# Gráfico de dispersión para visualizar la relación entre puntaje y otra variable (por ejemplo, población)
# Asegúrate de tener una columna para la variable con la que quieras correlacionar el puntaje.
if "Población" in df_filtrado_puntaje.columns:
    st.subheader("Relación entre Puntaje Promedio y Población")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="Población", y=selected_puntaje, data=df_filtrado_puntaje, hue="ESTU_DEPTO_RESIDE", palette="Set1")
    plt.title("Relación entre Puntaje Promedio y Población")
    plt.xlabel("Población")
    plt.ylabel("Puntaje Promedio")
    st.pyplot(plt)

# Gráfico de distribución del puntaje
st.subheader("Distribución de Puntajes Promedio")

plt.figure(figsize=(10, 6))
sns.histplot(df_filtrado_puntaje[selected_puntaje], bins=20, kde=True, color="blue")
plt.title("Distribución de Puntajes Promedio")
plt.xlabel("Puntaje Promedio")
plt.ylabel("Frecuencia")
st.pyplot(plt)
