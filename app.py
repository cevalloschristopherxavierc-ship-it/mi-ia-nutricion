import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN & ESTILO ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PREGUNTAS DE INICIO (PERFIL PERSONALIZADO) ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Bienvenido a Jarvis AI")
    st.subheader("Configura tu perfil para hoy:")
    with st.form("perfil_inicial"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Tu nombre?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Definición", "Rendimiento Fútbol"])
        if st.form_submit_button("🚀 INICIAR NÚCLEO"):
            st.session_state.u_nom, st.session_state.u_pes = nom, pes
            st.session_state.u_alt, st.session_state.u_obj = alt, obj
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. LÓGICA SEMANAL ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"📊 {st.session_state.u_pes}kg | {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    meta_k = 3000.0 if modo == "Fútbol (2h+)" else 2500.0
    
    agua = ((st.session_state.u_pes * 35) / 1000) + (1.0 if modo == "Fútbol (2h+)" else 0.5)
    st.info(f"💧 Agua: **{agua:.2f} L**")
    if st.button("🔄 Cambiar Perfil"):
        st.session_state.perfil_listo = False
        st.rerun()
