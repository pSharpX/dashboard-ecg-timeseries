# streamlit_ecg_dashboard.py
"""
Streamlit app: Visualización y análisis de ECG usando wfdb + neurokit2
- Lectura de registros WFDB (PhysioNet)
- Visualización en estilo "papel de EKG" con cuadricula calibrada (25 mm/s, 10 mm = 1 mV)
- Limpieza y detección de picos R con neurokit2
- Cálculo de frecuencia cardíaca y alertas (fuera de 60-100 lpm)

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
import io

st.set_page_config(page_title="ECG Dashboard (WFDB + NeuroKit2)", layout="wide")

# ---------------------- Helpers ----------------------

def read_wfdb_record(path: str):
    """Lee un registro WFDB usando wfdb.rdrecord.
    path puede ser un directorio+nombre relativo o un registro descargado localmente.
    Devuelve el objeto record y la matriz de señales p_signal.
    """
    record = wfdb.rdrecord(path)
    signal = record.p_signal  # shape (n_samples, n_leads)
    fs = int(record.fs)
    return record, signal, fs


def convert_to_mV(signal: np.ndarray, record) -> np.ndarray:
    """Intento de normalizar unidades a mV.
    - Si record.units existe y es 'uV' -> divide entre 1000
    - Si detecta que valores son demasiado grandes (>50) asume microvoltios y divide
    - Si record.adc_gain está disponible podría usarse (dejamos heurística).
    """
    units = None
    try:
        units = record.units
    except Exception:
        pass

    sig = signal.astype(float)
    # Heurística: si units indican microvoltios
    if units is not None:
        if any(["uv" in u.lower() or "micro" in u.lower() for u in units]):
            sig = sig / 1000.0
            return sig
    # si amplitud típica mayor a 50 -> probablemente uV
    if np.percentile(np.abs(sig), 99) > 50:
        sig = sig / 1000.0
    return sig


def plot_ecg_paper(ax, time, voltage, fs, lead_name="Lead", v_scale_mV_per_10mm=1.0):
    """Dibuja la señal sobre un 'papel de EKG' con cuadricula.
    - velocidad horizontal: 25 mm/s => 0.04 s/mm
    - vertical: 10 mm = 1 mV => 1 mm = 0.1 mV

    time: segundos
    voltage: mV
    """
    ax.plot(time, voltage, color='k', linewidth=1)
    ax.set_xlabel('Tiempo (s)')
    ax.set_ylabel('Voltaje (mV)')
    ax.set_title(lead_name)

    # Grid: cada 1 mm horizontal = 0.04 s; grand square = 5 mm -> 0.2 s
    major_x = 0.2
    minor_x = 0.04
    # vertical: 1 mm = 0.1 mV -> big square 0.5 mV
    major_y = 0.5
    minor_y = 0.1

    ax.xaxis.set_major_locator(MultipleLocator(major_x))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_x))
    ax.yaxis.set_major_locator(MultipleLocator(major_y))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_y))

    ax.grid(which='minor', linestyle=':', linewidth=0.5)
    ax.grid(which='major', linestyle='-', linewidth=1.0)

    # ajusta límites con algo de margen
    ax.set_xlim(time[0], time[-1])
    y_margin = (np.max(voltage) - np.min(voltage)) * 0.1 if np.ptp(voltage) > 0 else 0.5
    ax.set_ylim(np.min(voltage) - y_margin, np.max(voltage) + y_margin)

# ---------------------- UI ----------------------

st.title("Visualización y Análisis de Electrocardiograma (WFDB + NeuroKit2)")
st.markdown(
    """
    Este dashboard carga registros WFDB (ej. PhysioNet), muestra las derivaciones en papel de EKG
    y calcula la frecuencia cardiaca usando detección de picos R con NeuroKit2.

    Instrucciones rápidas:
    - Sube o indica la ruta del registro WFDB local (nombre base sin extensión).
    - Selecciona la derivación (lead) y ventana temporal a mostrar.
    - Ajusta la frecuencia de muestreo si es necesario (por defecto detectada del registro).
    """
)
st.sidebar.header("Controles")

# Input: Ruta/registro WFDB. El usuario puede subir archivos .dat/.hea también, pero aquí asumimos registro local.
record_path = st.sidebar.text_input("WFDB record path (ej: ./data/JS00001 o nombre-descargado)", value="./data/WFDBRecords/01/010/JS00001")

# Carga
col1, col2 = st.columns([2,1])
with col2:
    st.sidebar.markdown("\n")
    if st.sidebar.button("Cargar registro"):
        st.experimental_rerun()

# Intentamos leer
try:
    record, signals, fs = read_wfdb_record(record_path)
except Exception as e:
    st.error(f"No se pudo leer el registro WFDB: {e}")
    st.stop()

# Metadata
with st.expander("Metadata del registro (WFDB)"):
    md = {
        "record_name": getattr(record, 'record_name', 'n/a'),
        "fs": getattr(record, 'fs', 'n/a'),
        "sig_len": signals.shape[0],
        "n_leads": signals.shape[1] if signals.ndim>1 else 1,
        "sig_name": getattr(record, 'sig_name', [])
    }
    st.json(md)

# Convertir a mV si es necesario
signals_mV = convert_to_mV(signals, record)

# Derivadas disponibles
sig_names = getattr(record, 'sig_name', [f"L{i+1}" for i in range(signals_mV.shape[1])])
lead = st.sidebar.selectbox("Derivación", options=sig_names)
lead_idx = sig_names.index(lead)

# Ventana de tiempo a mostrar
total_seconds = signals_mV.shape[0] / fs
start_time = st.sidebar.number_input("Inicio (s)", min_value=0.0, max_value=float(total_seconds), value=0.0, step=0.5)
window_seconds = st.sidebar.number_input("Duración (s)", min_value=1.0, max_value=min(30.0, float(total_seconds)), value=10.0, step=1.0)

# Selección de segmento
start_sample = int(start_time * fs)
end_sample = int(min(signals_mV.shape[0], start_sample + window_seconds * fs))
segment = signals_mV[start_sample:end_sample, lead_idx]
time_vector = np.arange(start_sample, end_sample) / fs

# Visualización
st.subheader(f"Derivación: {lead} — ventana {start_time:.2f}–{start_time+window_seconds:.2f} s — fs={fs} Hz")

fig, ax = plt.subplots(figsize=(12, 4))
plot_ecg_paper(ax, time_vector, segment, fs, lead_name=lead)
st.pyplot(fig)

# Limpieza y detección de picos R con neurokit2
cleaned = nk.ecg_clean(segment, sampling_rate=fs, method="neurokit")

auth_signals, info = nk.ecg_peaks(cleaned, sampling_rate=fs, correct_artifacts=True)
peaks_idx = info.get('ECG_R_Peaks', np.array([]))

# Convertir picos a tiempos relativos al segmento
peaks_idx_segment = peaks_idx
peaks_times = peaks_idx_segment / fs

# Cálculo de intervalos RR y frecuencia cardiaca
if len(peaks_times) >= 2:
    rr_intervals = np.diff(peaks_times)  # en segundos
    instant_hr = 60.0 / rr_intervals  # lpm
    median_hr = float(np.median(instant_hr))
    mean_hr = float(np.mean(instant_hr))
else:
    rr_intervals = np.array([])
    instant_hr = np.array([])
    median_hr = None
    mean_hr = None

# Mostrar info
colA, colB, colC = st.columns(3)
with colA:
    st.metric("R-peaks detectados", int(len(peaks_times)))
with colB:
    st.metric("Frecuencia cardíaca (mediana) [lpm]", f"{median_hr:.1f}" if median_hr is not None else "n/a")
with colC:
    st.metric("Frecuencia cardíaca (media) [lpm]", f"{mean_hr:.1f}" if mean_hr is not None else "n/a")

# Alertas: fuera del rango 60-100 lpm
out_of_range = False
if median_hr is not None:
    if median_hr < 60:
        st.warning(f"Bradicardia detectada: frecuencia cardíaca mediana = {median_hr:.1f} lpm (<60)")
        out_of_range = True
    elif median_hr > 100:
        st.warning(f"Taquicardia detectada: frecuencia cardíaca mediana = {median_hr:.1f} lpm (>100)")
        out_of_range = True

# Mostrar la señal limpia y picos R sobreimpresos
fig2, ax2 = plt.subplots(figsize=(12, 3))
ax2.plot(time_vector, cleaned, linewidth=1, label='ECG cleaned')
ax2.scatter(peaks_times, cleaned[peaks_idx_segment], marker='v', color='red', label='R peaks')
ax2.set_xlabel('Tiempo (s)')
ax2.set_ylabel('mV')
ax2.legend()
st.pyplot(fig2)

# Tabla con intervalos RR e HR instantánea
if len(rr_intervals) > 0:
    df_rr = pd.DataFrame({
        'RR_interval_s': rr_intervals,
        'HR_lpm': instant_hr
    })
    st.subheader('Intervalos RR y frecuencia instantánea')
    st.dataframe(df_rr)
else:
    st.info('Se requieren al menos 2 picos R para calcular intervalos RR y frecuencia')

# Permitir descargar el segmento y las detecciones como CSV
export_btn = st.button('Exportar segmento y picos (CSV)')
if export_btn:
    out_df = pd.DataFrame({'time_s': time_vector, 'ecg_mV': cleaned})
    # marcar picos
    out_df['R_peak'] = 0
    out_df.loc[peaks_idx_segment, 'R_peak'] = 1
    csv = out_df.to_csv(index=False)
    st.download_button('Descargar CSV', data=csv, file_name='ecg_segment.csv', mime='text/csv')

st.markdown('---')
st.caption('App creada usando Streamlit, wfdb y NeuroKit2. Ajustar parámetros según calidad de los datos y calibración de cada registro.')
