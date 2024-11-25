import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

# Configuración de estilo del Dashboard
st.set_page_config(page_title="Dashboard de Puntajes", layout="wide")
st.title('Dashboard de Puntajes por Departamento')

# Definir la ruta del archivo Parquet
file_path = 'DatosParquet_reducido.parquet'  # Cambiado a ruta relativa

# Verificar si el archivo Parquet existe
if os.path.exists(file_path):
    # Cargar el archivo Parquet
    df = pd.read_parquet(file_path)

    # Filtrar los datos eliminando valores nulos en 'ESTU_DEPTO_RESIDE'
    df_filtrado = df.dropna(subset=['ESTU_DEPTO_RESIDE'])

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

    # Gráficos organizados en columnas
    col1, col2 = st.columns(2)

    # Gráfico de puntajes por departamento
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

            # Obtener el mejor y peor puntaje
            mejor_departamento = df_filtrado_puntaje.loc[df_filtrado_puntaje[selected_puntaje].idxmax()]
            peor_departamento = df_filtrado_puntaje.loc[df_filtrado_puntaje[selected_puntaje].idxmin()]

            # Mostrar el mejor y peor puntaje
            st.write(f"**Mejor Puntaje:**")
            st.write(f"Departamento: {mejor_departamento['ESTU_DEPTO_RESIDE']}, Puntaje: {mejor_departamento[selected_puntaje]:.2f}")
            st.write(f"**Peor Puntaje:**")
            st.write(f"Departamento: {peor_departamento['ESTU_DEPTO_RESIDE']}, Puntaje: {peor_departamento[selected_puntaje]:.2f}")
        else:
            st.warning("No hay departamentos seleccionados para mostrar el gráfico de puntajes.")

    # Gráfico de comparativa entre mejor y peor departamento
    with col2:
        st.subheader(f'Comparativa entre Mejor y Peor Puntaje por Departamento: {selected_puntaje}')
        df_comparativo = pd.DataFrame({
            'Departamento': [mejor_departamento['ESTU_DEPTO_RESIDE'], peor_departamento['ESTU_DEPTO_RESIDE']],
            'Puntaje': [mejor_departamento[selected_puntaje], peor_departamento[selected_puntaje]]
        })
        custom_palette = {mejor_departamento['ESTU_DEPTO_RESIDE']: '#006400', 
                          peor_departamento['ESTU_DEPTO_RESIDE']: '#8B0000'}
        plt.figure(figsize=(10, 6))
        bar_plot = sns.barplot(data=df_comparativo, y='Departamento', x='Puntaje', palette=custom_palette)
        plt.title(f'Comparativa entre Mejor y Peor Puntaje: {selected_puntaje}', fontsize=16, weight='bold')
        plt.xlabel(f'Media del {selected_puntaje}', fontsize=14, fontweight='bold')
        plt.ylabel('Departamento', fontsize=14, fontweight='bold')
        bar_plot.set_yticklabels(bar_plot.get_yticklabels(), fontsize=14, fontweight='bold')
        for p in bar_plot.patches:
            value = round(p.get_width(), 2)
            bar_plot.annotate(f'{value}', (p.get_width() / 2, p.get_y() + p.get_height() / 2.), ha='center', va='center', fontsize=14, fontweight='bold', color='white')
        plt.tight_layout()
        st.pyplot(plt)

    # Gráfico de radar para comparación entre mejor y peor departamento
    with st.container():
        st.subheader(f'Gráfico de Radar: Comparativa entre Mejor y Peor Departamento')
        radar_vars = ['FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE', 
                      'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR', 'FAMI_NUMLIBROS']
        radar_labels = [
            'Estrato Vivienda', 'Educación Padre', 'Educación Madre',
            'Internet en Hogar', 'Computadora', 'Número Libros'
        ]

        # Extraer datos normalizados
        normalizar = lambda x: (x - x.min()) / (x.max() - x.min())
        df_radar = df[radar_vars].apply(normalizar)
        mejor_data = df_radar.loc[df['ESTU_DEPTO_RESIDE'] == mejor_departamento['ESTU_DEPTO_RESIDE']].mean().tolist()
        peor_data = df_radar.loc[df['ESTU_DEPTO_RESIDE'] == peor_departamento['ESTU_DEPTO_RESIDE']].mean().tolist()

        # Cerrar los datos para el gráfico de radar
        angles = np.linspace(0, 2 * np.pi, len(radar_vars), endpoint=False).tolist()
        mejor_data += mejor_data[:1]
        peor_data += peor_data[:1]
        angles += angles[:1]

        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(7, 7), dpi=100, subplot_kw=dict(polar=True))
        ax.plot(angles, mejor_data, label=mejor_departamento['ESTU_DEPTO_RESIDE'], color='green', linewidth=2)
        ax.fill(angles, mejor_data, color='green', alpha=0.25)
        ax.plot(angles, peor_data, label=peor_departamento['ESTU_DEPTO_RESIDE'], color='red', linewidth=2)
        ax.fill(angles, peor_data, color='red', alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(radar_labels, fontsize=10)
        ax.set_title("Comparativa Normalizada", fontsize=14, weight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))

        st.pyplot(fig)
else:
    st.error("No se encontró el archivo de datos. Asegúrate de que esté en el directorio correcto.")
