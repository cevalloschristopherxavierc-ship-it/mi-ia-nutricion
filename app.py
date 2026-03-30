import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# 1. SEGURIDAD
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Configura los 'Secrets' en Streamlit Cloud.")
    st.stop()

# 2. ESTILOS DE LA PIZARRA (Vuelve el diseño que te gusta)
st.markdown("""
<style>
    .pizarra-fondo {
        background-color: #262626; border: 8px solid #59402a; border-radius: 15px;
        padding: 25px; color: white; font-family: monospace;
    }
    .pizarra-titulo { color: #00FF41; text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid #444; margin-bottom: 15px; }
    .pizarra-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 18px; }
    .pizarra-val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. SESIÓN DE USUARIO
if 'usuario' not in st.session_state: st.session_state.usuario = None
if 'kcal_dia' not in st.session_state: st.session_state.kcal_dia = 0.0

if st.session_state.usuario is None:
    with st.form("registro"):
        st.title("🦾 Jarvis Nutrición")
        nom = st.text_input("Tu Nombre:")
        ps = st.number_input("Peso Actual (kg):", value=70.0)
        al = st.number_input("Altura (cm):", value=170)
        if st.form_submit_button("Sincronizar Jarvis"):
            # Meta base: 30 kcal por kilo para mantenimiento/subida suave
            st.session_state.usuario = {"nombre": nom, "peso": ps, "meta_kcal": ps * 30, "meta_p": ps * 2}
            st.rerun()
    st.stop()

u = st.session_state.usuario

# 4. SIDEBAR CON BARRA DE PROGRESO VIVA
with st.sidebar:
    st.header(f"Agente: {u['nombre'].upper()}")
    # Cálculo de la barra
    porcentaje = min(st.session_state.kcal_dia / u['meta_kcal'], 1.0)
    st.write(f"🔥 Progreso Diario: {int(porcentaje * 100)}%")
    st.progress(porcentaje)
    st.write(f"Consumido: {int(st.session_state.kcal_dia)} / {int(u['meta_kcal'])} kcal")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# 5. DASHBOARD VISUAL
st.title("📈 Tu Panel de Control")
