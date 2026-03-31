import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel Xavier - Jarvis Core", page_icon="🦾", layout="wide")

# Estilo visual Premium
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

# --- 2. ESTADO INICIAL Y PREGUNTAS DE INICIO (PROHIBIDO CAMBIAR) ---
st.sidebar.title("🔋 PROTOCOLO DE INICIO")

# Preguntas de Despertar
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])

# Preguntas de Biometría (Tus detalles de inicio)
with st.sidebar.expander("📏 Datos Biométricos", expanded=True):
    estatura_cm = st.number_input("Estatura (cm):", min_value=100, max_value=250, value=175)
    peso_kg = st.number_input("Peso Actual (kg):", min_value=30.0, max_value=200.0, value=75.0)
    st.caption(f"Cálculos para: {estatura_cm}cm / {peso_kg}kg")

# --- 3. PANEL DE CONTROL: TODOS LOS DETALLES ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")

# Métricas Superiores
col_k, col_q, col_h = st.columns(3)
with col_k: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal Totales</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
with col_q: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)

# Hidratación con Barra de Progreso
with col_h:
    if 'agua' not in st.session_state: st.session_state.agua = 0
    progreso_agua = min(st.session_state.agua / 12, 1.0)
    st.markdown('<div class="metric-box"><p class="metric-label">💧 Hidratación</p></div>', unsafe_allow_html=True)
    st.progress(progreso_agua, text=f"{st.session_state.agua} / 12 vasos")

st.markdown(" ") # Espacio visual

# Macros Detallados
m1, m2, m3 = st.columns(3)
with m1: st.markdown('<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">0 / 160g</p></div>', unsafe_allow_html=True)
with m2: st.markdown('<div class="metric-box"><p class="metric-label">🍝 Carbohidratos</p><p class="metric-value">0 / 350g</p></div>', unsafe_allow_html=True)
with m3: st.markdown('<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">0 / 70g</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO MAESTRO DISCRETO ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización xavier2210"):
    master_key = st.text_input("Código Maestro:", type="password")
    if master_key == "xavier2210":
        es_maestro
