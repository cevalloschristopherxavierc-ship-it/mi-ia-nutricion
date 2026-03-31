import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel Xavier - Jarvis Core", page_icon="🦾", layout="wide")

# Estilo visual Premium (Igual a tu captura)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-label { font-size: 14px; color: #8b949e; margin-bottom: 2px; }
    .metric-value { font-size: 22px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ESTADO INICIAL (PROHIBIDO CAMBIAR) ---
st.sidebar.title("🔋 ESTADO INICIAL")
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])
    st.write(f"Sincronizando modo: {humor}")

# --- 3. PANEL DE CONTROL: TODOS TUS DETALLES ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")

# Primera fila de métricas (Energía y Quemado)
c1, c2, c3 = st.columns(3)
with c1: st.markdown('<div class="metric-box"><p class="metric-label">🔥 Kcal Totales</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado (Actividad)</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="metric-box"><p class="metric-label">💧 Hidratación</p><p class="metric-value">0 / 12 vasos</p></div>', unsafe_allow_html=True)

# Segunda fila de métricas (Macros Detallados)
m1, m2, m3 = st.columns(3)
with m1: st.markdown('<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">0 / 160g</p></div>', unsafe_allow_html=True)
with m2: st.markdown('<div class="metric-box"><p class="metric-label">🍝 Carbohidratos</p><p class="metric-value">0 / 350g</p></div>', unsafe_allow_html=True)
with m3: st.markdown('<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">0 / 70g</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO MAESTRO DISCRETO ---
st.markdown("---")
with st.expander("🔐 Sincronización xavier2210"):
    master_key = st.text_input("Código Maestro:", type="password")
    es_maestro
