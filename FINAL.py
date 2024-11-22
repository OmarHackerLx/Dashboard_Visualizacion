import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

# Definir la ruta del archivo Parquet
file_path = 'DatosParquet_reducido.parquet'  # Cambiado a ruta relativa

# Configuración de estilo
st.set_page_config(page_title="Dashboard de Puntajes", layout="wide")
st.title('Dashboard de Puntajes por Departamento')

# Verificar si el archivo Parquet existe
if os.path.exists(file_path):
    # Cargar el archivo Parquet
    df = pd.read_parquet(file_path)

    # Filtrar los datos eliminando valores nulos en 'ESTU_DEPTO_RESIDE'
    df_filtrado = df.dropna(subset=['ESTU_DEPTO_RESIDE'])

    # Crear un diccionario para mapear los valores de estratos a números (no se utilizará)
    estrato_mapping = {
        "Sin Estrato": None,
        "Estrato 1": 1,
        "Estrato 2": 2,
        "Estrato 3": 3,
        "Estrato 4": 4,
        "Estrato 5": 5,
        "Estrato 6": 6
    }

    # Reemplazar los valores de la columna 'FAMI_ESTRATOVIVIENDA' por valores numéricos (no se utilizará)
    df_filtrado['FAMI_ESTRATOVIVIENDA'] = df_filtrado['FAMI_ESTRATOVIVIENDA'].map(estrato_mapping)

    # Sidebar: Selección de puntaje y departamentos
    st.sidebar.header('Filtros del Dashboard')
    puntajes_columnas = ['PUNT_LECTURA_CRITICA', 'PUNT_MATEMATICAS', 'PUNT_C_NATURALES', 
                         'PUNT_SOCIALES_CIUDADANAS', 'PUNT_INGLES', 'PUNT_GLOBAL']
    selected_puntaje = st.sidebar.radio('Selecciona el puntaje a visualizar:', puntajes_columnas)

    # Agrupaciones y filtrado
    df_agrupado_puntajes = df.groupby('ESTU_DEPTO_RESIDE')[puntajes_columnas].mean().reset_index()
    departamentos = df_agrupado_puntajes['ESTU_DEPTO_RESIDE'].unique()
    selected_departamentos = st.sidebar.multiselect('Selecciona los departamentos:', options=departamentos, default=departamentos)

    df_filtrado_puntaje = df_agrupado_puntajes[df_agrupado_puntajes['ESTU_DEPTO_RESIDE'].isin(selected_departamentos)]

    # Obtener el mejor y peor puntaje
    mejor_departamento = df_filtrado_puntaje.loc[df_filtrado_puntaje[selected_puntaje].idxmax()]
    peor_departamento = df_filtrado_puntaje.loc[df_filtrado_puntaje[selected_puntaje].idxmin()]

    # Gráfico de barras comparando el mejor y peor departamento
    st.subheader(f'Comparativa entre Mejor y Peor Puntaje por Departamento: {selected_puntaje}')
    df_comparativo = pd.DataFrame({
        'Departamento': [mejor_departamento['ESTU_DEPTO_RESIDE'], peor_departamento['ESTU_DEPTO_RESIDE']],
        'Puntaje': [mejor_departamento[selected_puntaje], peor_departamento[selected_puntaje]]
    })

    # Crear una paleta personalizada (verde para el mejor puntaje, rojo para el peor)
    custom_palette = {mejor_departamento['ESTU_DEPTO_RESIDE']: '#006400', 
                      peor_departamento['ESTU_DEPTO_RESIDE']: '#8B0000'}

    # Crear el gráfico de barras horizontales con la paleta personalizada
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(data=df_comparativo, y='Departamento', x='Puntaje', palette=custom_palette)

    # Título llamativo con negrita
    plt.title(f'Comparativa entre Mejor y Peor Puntaje: {selected_puntaje}', fontsize=16, weight='bold', color='black')

    # Etiquetas de los ejes en negrita y tamaño 14
    plt.xlabel(f'Media del {selected_puntaje}', fontsize=14, fontweight='bold')
    plt.ylabel('Departamento', fontsize=14, fontweight='bold')

    # Cambiar tamaño de fuente de los nombres de los departamentos y ponerlos en negrita
    bar_plot.set_yticklabels(bar_plot.get_yticklabels(), fontsize=14, fontweight='bold', color='black')

    # Añadir los valores redondeados en el centro de las barras, en blanco
    for p in bar_plot.patches:
        value = round(p.get_width(), 2)  # Redondear el valor a 2 decimales
        bar_plot.annotate(f'{value}', 
                          (p.get_width() / 2, p.get_y() + p.get_height() / 2.),  # Posicionar en el centro de la barra
                          ha='center', va='center', fontsize=14, fontweight='bold', color='white')

    # Eliminar las líneas que afectan el fondo y la transparencia:
    # Quitar el fondo de la figura transparente y el fondo azul
    fig = plt.gcf()
    fig.patch.set_facecolor('white')  # Fondo blanco para la figura
    plt.gca().set_facecolor('white')  # Fondo blanco para los ejes

    # Hacer los números del eje X de tamaño 14
    plt.tick_params(axis='x', labelsize=14)  # Cambiar tamaño de los números del eje X

    # Ajustar el diseño para evitar el recorte de etiquetas
    plt.tight_layout()

    # Mostrar el gráfico
    st.pyplot(plt)
else:
    st.error("No se encontró el archivo de datos. Asegúrate de que esté en el directorio correcto.")
