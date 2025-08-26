# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 12:23:01 2025

@author: USER
"""

import streamlit as st
import pandas as pd
import wfdb
import os

dirname = os.path.dirname(__file__)

@st.cache_data
def read_records(dataset_path):
    filename = os.path.join(dirname, dataset_path)
    #'ludb/{}'.format(id)
    # WFDBRecords/01/010
    # 01-46
    # 010-019 ->> 10 each one
    try:
        return wfdb.rdsamp(filename)
    except FileNotFoundError:
        st.error(f"El archivo no se encontró: {filename}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error desconocido al cargar el archivo: {e}")
        return pd.DataFrame()

@st.cache_data
def read_dataset(dataset_path, separator=",", dtype=None):
    filename = os.path.join(dirname, dataset_path)
    try:
        return pd.read_csv(filename, sep=separator, dtype=dtype)
    except FileNotFoundError:
        st.error(f"El archivo no se encontró: {filename}")
        return pd.DataFrame()
    except pd.errors.ParserError:
        st.error(f"Hubo un error al analizar el archivo: {filename}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error desconocido al cargar el archivo: {e}")
        return pd.DataFrame()

@st.cache_data
def preprocess_data(df):
    # 1) Convertir FECHA_UTC a datetime
    df["FECHA"] = pd.to_datetime(df["FECHA_UTC"], format="%Y%m%d", errors="coerce")
    # 2) Extraer año/mes antes de convertir a string
    df["YEAR"]  = df["FECHA"].dt.year
    df["MONTH"] = df["FECHA"].dt.month
    # 3) Ahora formatear FECHA como texto legible
    df["FECHA"] = df["FECHA"].dt.strftime("%Y-%m-%d")

    # Manejo de horas
    df["HORA"] = pd.to_datetime(df["HORA_UTC"], format="%H%M%S", errors="coerce") \
                  .dt.strftime("%H:%M:%S")

    # Clasificaciones y estilos
    df["MAGNITUD_CLASS"]    = df["MAGNITUD"].apply(get_magnitud_category)
    df["PROFUNDIDAD_CLASS"] = df["PROFUNDIDAD"].apply(get_profundidad_category)
    df["SIZE"]              = df["MAGNITUD_CLASS"].apply(get_size)
    df["COLOR"]             = df["MAGNITUD_CLASS"].apply(get_color)
    df["COLOR_PREVIEW"]     = df["COLOR"].apply(get_color_preview)
    return df

@st.cache_data
def compute_metrics(df):
    total_sismos = len(df)
    avg_magnitud = df["MAGNITUD"].mean()
    max_magnitud = df["MAGNITUD"].max()
    return total_sismos, avg_magnitud, max_magnitud

def get_magnitud_category(magnitud):
    if pd.isna(magnitud): return "Desconocido"
    if magnitud < 2:   return "Micro"
    if magnitud < 4:   return "Menor"
    if magnitud < 5:   return "Ligero"
    if magnitud < 6:   return "Moderado"
    if magnitud < 7:   return "Fuerte"
    if magnitud < 8:   return "Mayor"
    if magnitud < 10:  return "Épico o Catastrófico"
    return "Legendario o apocalíptico"

def get_profundidad_category(profundidad):
    if pd.isna(profundidad): return "Desconocido"
    if profundidad <= 70:    return "Superficial"
    if profundidad <= 450:   return "Intermedio"
    return "Profundo"

def get_size(magnitud_class):
    return {
        "Micro": 0.2*100*10,
        "Menor": 0.4*100*10,
        "Ligero": 0.8*100*10,
        "Moderado": 1*100*10,
        "Fuerte": 10*100*10,
        "Mayor": 15*100*10,
        "Épico o Catastrófico": 30*100*10,
        "Legendario o apocalíptico": 30*100*10
    }.get(magnitud_class)

def get_color(magnitud_class):
    return {
        "Micro": "#008f39",
        "Menor": "#ffff00",
        "Ligero": "#ff6600",
        "Moderado": "#ff4500",
        "Fuerte": "#ff4000",
        "Mayor": "#b83d14",
        "Épico o Catastrófico": "#572364",
        "Legendario o apocalíptico": "#0a0a0a",
        "Desconocido": "#888888"
    }.get(magnitud_class, "#000000")

def get_color_preview(color):
    c = color.lstrip('#')
    return (f'data:image/svg+xml;utf8,'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
            f'<circle cx="40" cy="50" r="25" fill="%23{c}"/></svg>')
