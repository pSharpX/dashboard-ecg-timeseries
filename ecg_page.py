# streamlit_ecg_dashboard.py
"""
Streamlit app: Visualización y análisis de ECG usando wfdb + neurokit2
- Lectura de registros WFDB (PhysioNet)
- Visualización en estilo "papel de EKG" con cuadricula calibrada (25 mm/s, 10 mm = 1 mV)
- Limpieza y detección de picos R con neurokit2
- Cálculo de frecuencia cardíaca y alertas (fuera de 60-100 lpm)
- Página adicional para mostrar las 12 derivaciones completas en formato 3x4
- Muestra metadata del paciente en la barra lateral izquierda

Requisitos:
    pip install streamlit wfdb neurokit2 matplotlib numpy pandas plotly

Ejecutar:
    streamlit run streamlit_ecg_dashboard.py

Diseñado para dataset: "A large scale 12-lead electrocardiogram database for arrhythmia study"
"""

import streamlit as st
import numpy as np
import pandas as pd
import wfdb
import neurokit2 as nk
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

st.set_page_config(page_title="ECG Dashboard (WFDB + NeuroKit2)", layout="wide")

# ---------------------- Helpers ----------------------

def read_wfdb_record(path: str):
    record = wfdb.rdrecord(path)
    signal = record.p_signal  # shape (n_samples, n_leads)
    fs = int(record.fs)
    return record, signal, fs


def convert_to_mV(signal: np.ndarray, record) -> np.ndarray:
    sig = signal.astype(float)
    try:
        units = record.units
        if any(["uv" in u.lower() or "micro" in u.lower() for u in units]):
            sig = sig / 1000.0
            return sig
    except Exception:
        pass
    if np.percentile(np.abs(sig), 99) > 50:
        sig = sig / 1000.0
    return sig


def plot_ecg_paper(ax, time, voltage, lead_name="Lead"):
    ax.plot(time, voltage, color='k', linewidth=1)
    ax.set_title(lead_name, fontsize=8)

    major_x = 0.2
    minor_x = 0.04
    major_y = 0.5
    minor_y = 0.1

    ax.xaxis.set_major_locator(MultipleLocator(major_x))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_x))
    ax.yaxis.set_major_locator(MultipleLocator(major_y))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_y))

    ax.grid(which='minor', linestyle=':', linewidth=0.5)
    ax.grid(which='major', linestyle='-', linewidth=1.0)

    ax.set_xlim(time[0], time[-1])
    y_margin = (np.max(voltage) - np.min(voltage)) * 0.1 if np.ptp(voltage) > 0 else 0.5
    ax.set_ylim(np.min(voltage) - y_margin, np.max(voltage) + y_margin)

# ---------------------- Main ----------------------

st.title("Visualización y Análisis de Electrocardiograma (WFDB + NeuroKit2)")
st.markdown(
    """
    Este dashboard carga registros WFDB (ej. PhysioNet), muestra las derivaciones en papel de EKG
    y calcula la frecuencia cardiaca usando detección de picos R con NeuroKit2.
    """
)
st.sidebar.header("Navegación")
page = st.sidebar.radio("Selecciona página:", ["Una derivación", "12 derivaciones"])

record_path = st.sidebar.text_input("WFDB record path", value="./data/WFDBRecords/01/010/JS00001")

try:
    record, signals, fs = read_wfdb_record(record_path)
except Exception as e:
    st.error(f"No se pudo leer el registro WFDB: {e}")
    st.stop()

signals_mV = convert_to_mV(signals, record)
sig_names = getattr(record, 'sig_name', [f"L{i+1}" for i in range(signals_mV.shape[1])])

# Mostrar metadata del paciente en la barra lateral
st.sidebar.markdown("---")
st.sidebar.subheader("Metadata del paciente")
patient_info = {}
try:
    patient_info["Nombre del registro"] = getattr(record, 'record_name', 'n/a')
    patient_info["Frecuencia de muestreo"] = getattr(record, 'fs', 'n/a')
    patient_info["Longitud de señal"] = signals.shape[0]
    patient_info["Número de derivaciones"] = signals.shape[1] if signals.ndim > 1 else 1
    patient_info["Derivaciones"] = ", ".join(sig_names)
except Exception:
    pass
st.sidebar.json(patient_info)

# Parámetros de ventana de tiempo
total_seconds = signals_mV.shape[0] / fs
start_time = st.sidebar.number_input("Inicio (s)", min_value=0.0, max_value=float(total_seconds), value=0.0, step=0.5)
window_seconds = st.sidebar.number_input("Duración (s)", min_value=1.0, max_value=min(30.0, float(total_seconds)), value=10.0, step=1.0)

start_sample = int(start_time * fs)
end_sample = int(min(signals_mV.shape[0], start_sample + window_seconds * fs))
time_vector = np.arange(start_sample, end_sample) / fs

if page == "Una derivación":
    lead = st.sidebar.selectbox("Derivación", options=sig_names)
    lead_idx = sig_names.index(lead)
    segment = signals_mV[start_sample:end_sample, lead_idx]

    st.subheader(f"Derivación: {lead} — ventana {start_time:.2f}–{start_time+window_seconds:.2f} s — fs={fs} Hz")

    fig, ax = plt.subplots(figsize=(12, 4))
    plot_ecg_paper(ax, time_vector, segment, lead_name=lead)
    st.pyplot(fig)

    cleaned = nk.ecg_clean(segment, sampling_rate=fs, method="neurokit")
    _, info = nk.ecg_peaks(cleaned, sampling_rate=fs, correct_artifacts=True)
    peaks_idx = info.get('ECG_R_Peaks', np.array([]))
    peaks_times = peaks_idx / fs

    if len(peaks_times) >= 2:
        rr_intervals = np.diff(peaks_times)
        instant_hr = 60.0 / rr_intervals
        median_hr = float(np.median(instant_hr))
        mean_hr = float(np.mean(instant_hr))
    else:
        median_hr, mean_hr = None, None

    colA, colB = st.columns(2)
    with colA:
        st.metric("R-peaks detectados", int(len(peaks_times)))
    with colB:
        st.metric("Frecuencia cardíaca mediana [lpm]", f"{median_hr:.1f}" if median_hr else "n/a")

    if median_hr:
        if median_hr < 60:
            st.warning(f"Bradicardia detectada: {median_hr:.1f} lpm")
        elif median_hr > 100:
            st.warning(f"Taquicardia detectada: {median_hr:.1f} lpm")

    fig2, ax2 = plt.subplots(figsize=(12, 3))
    ax2.plot(time_vector, cleaned, linewidth=1, label='ECG cleaned')
    ax2.scatter(peaks_times, cleaned[peaks_idx], marker='v', color='red', label='R peaks')
    ax2.legend()
    st.pyplot(fig2)

elif page == "12 derivaciones":
    st.subheader(f"Todas las derivaciones (12 leads) — ventana {start_time:.2f}–{start_time+window_seconds:.2f} s")
    n_leads = min(12, signals_mV.shape[1])
    fig, axes = plt.subplots(3, 4, figsize=(16, 9), sharex=True)
    axes = axes.flatten()
    for i in range(n_leads):
        segment = signals_mV[start_sample:end_sample, i]
        plot_ecg_paper(axes[i], time_vector, segment, lead_name=sig_names[i])
    plt.tight_layout()
    st.pyplot(fig)

st.caption('App creada con Streamlit, wfdb y NeuroKit2.')
