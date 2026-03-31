import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core v2.2", page_icon="🦾", layout="wide")

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #00d4ff; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00d4ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROTOCOLO DE INICIO (PREGUNTAS EN BARRA LATERAL) ---
st.sidebar.title("🔋 ESTADO DEL SISTEMA")
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia =
