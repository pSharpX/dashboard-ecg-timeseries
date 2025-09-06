# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 08:24:01 2025

@author: USER
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import helpers as utils
import numpy as np
import wfdb
import neurokit2 as nk

# Configuración de la app
st.set_page_config(page_title="Visualización y Análisis de Electrocardiograma", layout="wide")

# Cabecera
st.title("Visualización y Análisis de Electrocardiograma")
st.markdown("""
Este dashboard interactivo permite explorar más de 60 años de actividad sísmica registrada en el Perú.  
Puedes aplicar filtros para visualizar sismos según el **año**, la **magnitud** o la **profundidad** del epicentro.

🔍 Usa la barra lateral para ajustar los parámetros de búsqueda.  
📍 Visualiza los eventos en un mapa interactivo o revisa los datos agrupados por año.
""")
st.divider()

# Carga y preprocesamiento

derivadas = ['i', 'ii', 'iii', 'avr', 'avl', 'avf', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6']

record = utils.read_records("./data/WFDBRecords/01/010/JS00001")
signal = record[0]
metadata = record[1]

data = pd.DataFrame(metadata.values(), index=metadata.keys())

st.dataframe(data)

derivada = "i"
señal = signal[:, derivadas.index(derivada)]/1000 #hay un bug aqui / corregir
tiempo = np.linspace(0, 10, 5000)

fig_conv = plt.figure(figsize=(30,12))
plt.plot(tiempo, señal, color='k', label=derivada, linewidth=3)
plt.legend(loc=1)

st.pyplot(fig_conv)

#ecg = nk.ecg_simulate(duration=10, sampling_rate=1000)
ecg = señal
signals = pd.DataFrame({"ECG_Raw" : ecg,
                        "ECG_NeuroKit" : nk.ecg_clean(ecg, sampling_rate=1000, method="neurokit"),
                        "ECG_BioSPPy" : nk.ecg_clean(ecg, sampling_rate=1000, method="biosppy"),
                        "ECG_PanTompkins" : nk.ecg_clean(ecg, sampling_rate=1000, method="pantompkins1985"),
                        "ECG_Hamilton" : nk.ecg_clean(ecg, sampling_rate=1000, method="hamilton2002"),
                        "ECG_Elgendi" : nk.ecg_clean(ecg, sampling_rate=1000, method="elgendi2010"),
                        "ECG_EngZeeMod" : nk.ecg_clean(ecg, sampling_rate=1000, method="engzeemod2012")})

#signals.plot()


fig_conv2 = plt.figure(figsize=(30,12))
plt.plot(signals["ECG_Raw"], color='k', label=derivada, linewidth=3)

st.dataframe(signals)

st.pyplot(fig_conv2)

#ecg = nk.ecg_simulate(duration=10, sampling_rate=1000)
cleaned = nk.ecg_clean(ecg, sampling_rate=1000)
signals2, info = nk.ecg_peaks(cleaned, correct_artifacts=True)
fig2 = nk.events_plot(info["ECG_R_Peaks"], cleaned)


st.pyplot(fig2)