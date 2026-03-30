import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

# --- 2. SEGURIDAD (SECRETS) ---
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ ERROR: Configura SUPABASE_URL, SUPABASE_KEY y GEMINI_API_KEY en Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS CSS ---
st.markdown("""
<style>
    .pizarra-fondo {
        background-color: #1e1e1e; border: 5px solid #59402a; border-radius: 15px;
        padding: 20px; color: white; font-family: 'Courier New', monospace;
    }
    .pizarra-titulo { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 2px solid #333; margin-bottom: 15px; }
    .pizarra-dato { display: flex; justify-content: space-between; font-size: 18px; margin: 5px 0; }
    .val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. MANEJO DE SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0
if 'nombre_user' not in st.session_state: st.session_state.nombre_user = "Agente"

# --- 5. SIDEBAR (PROGRESO) ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    st.session_state.nombre_user = st.text_input("Nombre de Agente:", value=st.session_state.nombre_user)
    meta = st.number_input("Meta Kcal Diaria:", value=2500)
    
    progreso = min(st.session_state.kcal_total / meta, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    st.write(f"Consumido: {int(st.session_state.kcal_total)} / {meta} kcal")
    
    if st.button("🔄 Reiniciar Día"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 6. CUERPO PRINCIPAL (DASHBOARD) ---
st.title("📈 Tu Panel de Control")

# Pestañas para organizar
tab_progreso, tab_registro = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR COMIDA"])

with tab_progreso:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Calorías Semanales")
        df_cal = pd.DataFrame({'Día': ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB', 'DOM'], 'Kcal': [2530, 2250, 2310, 2440, 2630, 2350, 2500]})
        st.plotly_chart(
