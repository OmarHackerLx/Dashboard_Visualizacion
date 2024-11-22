import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from math import pi

# Asegúrate de que tu DataFrame 'df' ya esté filtrado y procesado según los pasos previos

# Definir las columnas de puntajes disponibles
puntajes_columnas = ['PUNT_LECTURA_CRITICA', 'PUNT_MATEMATICAS', 'PUNT_C_NATURALES', 
                     'PUNT_SOCIALES_CIUDADANAS', 'PUNT_INGLES', 'PUNT_GLOBAL']
selected_puntaje = st.sidebar.radio('Selecciona el puntaje a visualizar:', puntajes_columnas)

# Agrupar los datos por departamento y calcular la media de cada puntaje
df_agrupado_puntajes = df.groupby('ESTU_DEPTO_RESIDE')[puntajes_columnas].mean().reset_index()

# Filtrar el mejor y peor departamento según el puntaje seleccionado
mejor_departamento = df_agrupado_puntajes.loc[df_agrupado_puntajes[selected_puntaje].idxmax()]
peor_departamento = df_agrupado_puntajes.loc[df_agrupado_puntajes[selected_puntaje].idxmin()]

# Extraer las variables relevantes para el gráfico de radar
# Suponemos que tienes las mismas columnas para las variables como en tu código de radar
df_radar = df[['ESTU_DEPTO_RESIDE', 'FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
               'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']]

# Filtrar los datos de los mejores y peores departamentos
mejor_depto = df_radar[df_radar['ESTU_DEPTO_RESIDE'] == mejor_departamento['ESTU_DEPTO_RESIDE']].mean()
peor_depto = df_radar[df_radar['ESTU_DEPTO_RESIDE'] == peor_departamento['ESTU_DEPTO_RESIDE']].mean()

# Normalizar los datos de los dos departamentos seleccionados (usar Min-Max Normalization)
def normalizar(df_radar):
    return (df_radar - df_radar.min()) / (df_radar.max() - df_radar.min())

mejor_depto_normalizado = normalizar(mejor_depto)
peor_depto_normalizado = normalizar(peor_depto)

# Etiquetas descriptivas
nuevas_etiquetas = [
    'Estrato de Vivienda', 
    'Nivel Educativo del Padre', 
    'Nivel Educativo de la Madre', 
    'Acceso a Internet', 
    'Disponibilidad de Computadora', 
    'Número de Libros del Hogar'
]

# Preparar los datos para el gráfico de radar
mejor_depto_vals = mejor_depto_normalizado.tolist()
peor_depto_vals = peor_depto_normalizado.tolist()

# Número de categorías
num_vars = len(nuevas_etiquetas)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # Cerrar el gráfico

mejor_depto_vals += mejor_depto_vals[:1]
peor_depto_vals += peor_depto_vals[:1]

# Crear gráfico de radar
fig, ax = plt.subplots(figsize=(7, 7), dpi=100, subplot_kw=dict(polar=True))

# Gráfico de radar para el mejor departamento
ax.plot(angles, mejor_depto_vals, color='green', linewidth=2, linestyle='solid', label=f'Mejor Departamento: {mejor_departamento["ESTU_DEPTO_RESIDE"]}')
ax.fill(angles, mejor_depto_vals, color='green', alpha=0.25)

# Gráfico de radar para el peor departamento
ax.plot(angles, peor_depto_vals, color='red', linewidth=2, linestyle='solid', label=f'Peor Departamento: {peor_departamento["ESTU_DEPTO_RESIDE"]}')
ax.fill(angles, peor_depto_vals, color='red', alpha=0.25)

# Añadir etiquetas con letras negras y tamaño 10
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(nuevas_etiquetas, fontsize=10, color='black', fontweight='bold')  # Etiquetas con tamaño 10

# Título y leyenda con tamaño de letra 10
ax.set_title(f'Comparación Normalizada: Mejor vs Peor Departamento por {selected_puntaje}', fontsize=12, color='black', fontweight='bold', y=1.1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=10, frameon=True, shadow=True, fancybox=True)  # Leyenda con tamaño 10

# Ajustar el diseño para evitar recortes
plt.tight_layout()

# Mostrar el gráfico con Streamlit
st.subheader(f'Gráfico de Radar: Comparación de {selected_puntaje}')
st.pyplot(fig)
