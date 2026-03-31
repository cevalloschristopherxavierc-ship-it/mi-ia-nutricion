import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core - Panel Xavier", page_icon="🦾", layout="wide")

# Estilo visual de tu captura
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-label { font-size: 16px; color: #8b949e; }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE ACCESO SEGÚN ROL ---
if 'rol' not in st.session_state:
    st.session_state.rol = None

if st.session_state.rol is None:
    st.title("🔐 Sincronización de Núcleo")
    u_cod = st.text_input("Introduce Código de Acceso:", type="password")
    if st.button("CONECTAR"):
        if u_cod == "xavier2210":
            st.session_state.rol = "MAESTRO"
            st.rerun()
        elif u_cod == "invitado2026": # Código para tus amigos
            st.session_state.rol = "INVITADO"
            st.rerun()
        else:
            st.error("Código no reconocido por Jarvis.")
    st.stop()

# --- 3. PANEL DE MÉTRICAS (SOLO VISIBLE PARA XAVIER) ---
st.title(f"🦾 {st.session_state.rol}: Panel de Control")

if st.session_state.rol == "MAESTRO":
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-box"><p class="metric-label">🍗 Prot (g)</p><p class="metric-value">0 / 160</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)
else:
    st.info("👋 ¡Bienvenido! Estás en modo Invitado. Puedes explorar las funciones generales, pero los datos de Xavier están protegidos.")

st.markdown("---")

# ---
