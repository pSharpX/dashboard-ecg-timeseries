# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 08:24:01 2025

@author: USER
"""

#streamlit run catalogo_sismico_page.py

import streamlit as st
import pandas as pd
import plotly.express as px
import helpers as utils

# Configuración de la app
st.set_page_config(page_title="Catálogo Sísmico del Perú", layout="wide")

# Cabecera
st.title("🌎 Catálogo Sísmico del Perú (1960 - 2023)")
st.markdown("""
Este dashboard interactivo permite explorar más de 60 años de actividad sísmica registrada en el Perú.  
Puedes aplicar filtros para visualizar sismos según el **año**, la **magnitud** o la **profundidad** del epicentro.

🔍 Usa la barra lateral para ajustar los parámetros de búsqueda.  
📍 Visualiza los eventos en un mapa interactivo o revisa los datos agrupados por año.
""")
st.divider()

# Carga y preprocesamiento
raw = utils.read_dataset("./data/Catalogo1960_2023.csv",
                         dtype={"ID":"int64","FECHA_UTC":str,"HORA_UTC":str,
                                "LATITUD":"float64","LONGITUD":"float64","PROFUNDIDAD":"int64",
                                "MAGNITUD":"float64","FECHA_CORTE":str})
df = utils.preprocess_data(raw)

# Dataframe inicial
column_config = {
    "FECHA": st.column_config.TextColumn("Fecha"),
    "HORA": "Hora",
    "LATITUD": "Latitud",
    "LONGITUD": "Longitud",
    "PROFUNDIDAD": st.column_config.NumberColumn("Profundidad (Km)"),
    "MAGNITUD": st.column_config.TextColumn("Magnitud"),
    "MAGNITUD_CLASS": "Clase",
    "PROFUNDIDAD_CLASS": "Clase",
    "COLOR_PREVIEW": st.column_config.ImageColumn("Color")
}

# Ordenamos solo la tabla por la fecha de manera descendente
df_sorted = df.sort_values(by="FECHA", ascending=False)

st.dataframe(df_sorted,
             hide_index=True,
             column_config=column_config,
             column_order=("FECHA","HORA","LATITUD","LONGITUD",
                           "MAGNITUD","MAGNITUD_CLASS","PROFUNDIDAD","PROFUNDIDAD_CLASS","COLOR_PREVIEW"))

# Filtros
st.sidebar.header("🎛️ Filtros")
years = df["YEAR"].unique()
mags = df["MAGNITUD_CLASS"].unique()
profs = df["PROFUNDIDAD_CLASS"].unique()

start_year, end_year = st.sidebar.select_slider(
    "Años", options=years, value=(years.min(), years.max())
)
mags_sel = st.sidebar.multiselect("Magnitud", options=mags, default=mags)
profs_sel = st.sidebar.multiselect("Profundidad", options=profs, default=profs)

df1 = df[(df.YEAR.between(start_year, end_year)) &
         (df.MAGNITUD_CLASS.isin(mags_sel)) &
         (df.PROFUNDIDAD_CLASS.isin(profs_sel))]

# Métricas
total_sismos, avg_magnitud, max_magnitud = utils.compute_metrics(df1)
col1, col2, col3 = st.columns(3)
col1.metric("Total de Sismos", f"{total_sismos:,}")
col2.metric("Magnitud Promedio", f"{avg_magnitud:.2f}")

# Extraer fecha máxima ya como string
if not df1.empty:
    fecha_max = df1.loc[df1.MAGNITUD.idxmax(), 'FECHA']
else:
    fecha_max = "N/A"

col3.metric(
    "Magnitud Máxima",
    f"{max_magnitud:.2f}",
    help=f"Fecha: {fecha_max}"
)

# Resultados y gráficos
st.markdown(f"**Filtros:** Años {start_year}-{end_year} | Magnitudes {mags_sel} | Profundidades {profs_sel}")

tab1, tab2 = st.tabs(["🗺️ Mapa", "📊 Por Año"])
with tab1:
    st.subheader("Mapa de Sismos en Perú")
    color_map = {
        "Micro":"#008f39","Menor":"#ffff00","Ligero":"#ff6600",
        "Moderado":"#ff4500","Fuerte":"#ff4000","Mayor":"#b83d14",
        "Épico o Catastrófico":"#572364","Legendario o apocalíptico":"#0a0a0a"
    }
    fig = px.scatter_mapbox(
        df1, lat="LATITUD", lon="LONGITUD",
        color="MAGNITUD_CLASS", size="SIZE",
        hover_data={
        "FECHA": True,
        "HORA": True,
        "MAGNITUD": True,
        "PROFUNDIDAD": True,
        "LATITUD": False,
        "LONGITUD": False,
        "SIZE": False,
        "MAGNITUD_CLASS": False
        },
        color_discrete_map=color_map,
        size_max=15, zoom=5,
        center={"lat":-9.19,"lon":-75.02}
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
with tab2:
    st.subheader("Sismos por Año")

    # Asegurar que YEAR sea tipo int
    df2 = df1.copy()
    df2["YEAR"] = df2["YEAR"].astype(int)

    # Agrupar por año
    df2 = df2.groupby("YEAR").size().reset_index(name="COUNT")

    # Verificar si hay datos
    if not df2.empty:
        # Calcular máximo
        max_value = df2["COUNT"].max()
        max_year = df2[df2["COUNT"] == max_value]["YEAR"].values[0]

        # Colores personalizados
        colors = ['blue' if year == max_year else 'indianred' for year in df2["YEAR"]]
        
        # Mensaje
        st.info(f"📌 En el rango de años analizado, el año con más sismos fue **{max_year}**, con un total de **{max_value}** sismos registrados.")
        
        # Gráfico
        fig2 = px.bar(
            df2, x="YEAR", y="COUNT",
            labels={"COUNT": "Sismos", "YEAR": "Año"},
            text_auto=True,
            template="plotly_white"
        )
        fig2.update_traces(marker_color=colors)
        st.plotly_chart(fig2, use_container_width=True)

        # Tabla
        st.dataframe(df2, hide_index=True,
                     column_config={"YEAR": "Año", "COUNT": "Cantidad"})

        
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar. Intenta seleccionar una magnitud o profundidad.")


    

st.divider()
st.header("🧠 Conclusiones e Insights Clave")

st.markdown("""
Este panel busca ofrecer una interpretación sencilla de los datos sísmicos del Perú, recogidos por el Instituto Geofísico del Perú (IGP) desde 1960. A continuación, se presentan algunos patrones clave que pueden resultar útiles para la ciudadanía, investigadores y autoridades:

#### 📌 1. ¿Con qué frecuencia se registran sismos fuertes?
A través del gráfico de barras de **magnitud promedio por década**, podemos observar si los eventos sísmicos más intensos han aumentado o disminuido con el tiempo.  
> 💡 *Se observa que, aunque la actividad sísmica es constante, la magnitud promedio se ha mantenido relativamente estable en las últimas décadas.*

#### 📌 2. ¿Qué tan profunda suele ser la actividad sísmica?
La profundidad a la que ocurren los sismos influye en qué tanto se sienten en la superficie. El gráfico de dispersión muestra cómo se distribuyen los sismos en cuanto a su magnitud y profundidad.  
> 💡 *Los sismos más intensos tienden a ocurrir a profundidades intermedias (entre 70 y 150 km).*

#### 📌 3. ¿Existen patrones según el tipo de magnitud?
El tipo de magnitud calculada también puede darnos pistas sobre el tipo de energía liberada.  
> 💡 *Las diferentes clases de magnitud están distribuidas a lo largo del país, pero algunas tienden a concentrarse a ciertas profundidades.*

#### ⚠️ Consideraciones:
- **Este dashboard no reemplaza estudios científicos**, pero puede ayudar a orientar preguntas clave o decisiones iniciales.
- La costa peruana sigue siendo una **zona de riesgo sísmico alto**, por lo que se recomienda continuar con medidas de prevención y educación.
""")

# Gráfico 1: Magnitud promedio por década
df1["DECADE"] = (df1["YEAR"] // 10) * 10
mag_decade = df1.groupby("DECADE")["MAGNITUD"].mean().reset_index()
fig3 = px.bar(mag_decade, x="DECADE", y="MAGNITUD",
              labels={"MAGNITUD":"Magnitud Promedio", "DECADE":"Década"},
              text_auto=".2f", template="plotly_white",
              title="📊 Magnitud Promedio por Década")
fig3.update_traces(marker_color='royalblue')
st.plotly_chart(fig3, use_container_width=True)

# Gráfico 2: Relación magnitud vs. profundidad
fig4 = px.scatter(df1, x="PROFUNDIDAD", y="MAGNITUD",
                  color="MAGNITUD_CLASS", size="MAGNITUD",
                  labels={"PROFUNDIDAD":"Profundidad (Km)", "MAGNITUD":"Magnitud"},
                  title="🔍 Relación entre Magnitud y Profundidad")
fig4.update_layout(template="plotly_white")
st.plotly_chart(fig4, use_container_width=True)

# Mensaje interpretativo
st.info("💡 Se observa que los sismos con mayor magnitud suelen tener profundidades intermedias. Además, en la última década, la magnitud promedio se ha mantenido estable.")
