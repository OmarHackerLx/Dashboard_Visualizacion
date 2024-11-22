# Mostrar el gráfico comparativo de puntajes entre el mejor y el peor departamento
if not df_filtrado_puntaje.empty:
    # Obtener el mejor y peor puntaje
    mejor_departamento = df_filtrado_puntaje.loc[df_filtrado_puntaje[selected_puntaje].idxmax()]
    peor_departamento = df_filtrado_puntaje.loc[df_filtrado_puntaje[selected_puntaje].idxmin()]

    # Crear un DataFrame con los datos de los mejores y peores departamentos
    df_comparativo = pd.DataFrame({
        'ESTU_DEPTO_RESIDE': [mejor_departamento['ESTU_DEPTO_RESIDE'], peor_departamento['ESTU_DEPTO_RESIDE']],
        selected_puntaje: [mejor_departamento[selected_puntaje], peor_departamento[selected_puntaje]]
    })

    # Configuración del gráfico de barras para los mejores y peores departamentos
    plt.figure(figsize=(14, 8))

    # Crear la paleta personalizada para los colores
    custom_palette_comparativo = {
        mejor_departamento['ESTU_DEPTO_RESIDE']: '#006400',  # Verde para el mejor
        peor_departamento['ESTU_DEPTO_RESIDE']: '#8B0000'   # Rojo para el peor
    }

    # Crear el gráfico de barras
    bar_plot_comparativo = sns.barplot(data=df_comparativo, y='ESTU_DEPTO_RESIDE', x=selected_puntaje, palette=custom_palette_comparativo)

    # Título llamativo con negrita
    plt.title(f'Comparativa de {selected_puntaje} - Mejor vs Peor Departamento', fontsize=18, weight='bold', color='black')

    # Etiquetas de los ejes en negrita y tamaño 16
    plt.xlabel(f'Media de {selected_puntaje}', fontsize=16, fontweight='bold')
    plt.ylabel('Departamento', fontsize=16, fontweight='bold')

    # Cambiar tamaño de fuente de los nombres de los departamentos y ponerlos en negrita
    bar_plot_comparativo.set_yticklabels(bar_plot_comparativo.get_yticklabels(), fontsize=16, fontweight='bold', color='black')

    # Añadir los valores redondeados en el centro de las barras
    for p in bar_plot_comparativo.patches:
        value = round(p.get_width())  # Redondear el valor a entero
        bar_plot_comparativo.annotate(f'{value}', 
                                     (p.get_width() / 2, p.get_y() + p.get_height() / 2.),  # Posicionar en el centro de la barra
                                     ha='center', va='center', fontsize=16, fontweight='bold', color='white')

    # Eliminar las líneas que afectan el fondo y la transparencia
    fig_comparativo = plt.gcf()
    fig_comparativo.patch.set_facecolor('white')  # Fondo blanco para la figura
    plt.gca().set_facecolor('white')  # Fondo blanco para los ejes

    # Ajustar el diseño para evitar el recorte de etiquetas
    plt.tight_layout()

    # Mostrar el gráfico comparativo
    st.pyplot(plt)
    plt.close()
else:
    st.warning("No se puede mostrar la comparativa sin datos de puntajes.")
