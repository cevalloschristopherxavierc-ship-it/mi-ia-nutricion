import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIG & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Fit Xavier", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. SESIÓN & PREGUNTAS ---
if 'k_t' not in st.session_state:
    for k in ['k_t', 'p_t', 'c_t', 'g_t']: st.session_state[k] = 0.0

# --- 3. SIDEBAR (PERFIL & HIDRATACIÓN) ---
with st.sidebar:
    st.title("🦾 NÚCLEO DE JARVIS")
    u_nom = "Xavier"
    
    # Fecha Actual
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    hoy_idx = datetime.now().weekday()
    st.subheader(f"📅 Hoy es {dias[hoy_idx]}")
    
    # Preguntas de Inicio
    st.write("---")
    st.subheader("📋 Estado Actual")
    sueño = st.slider("¿Cómo dormiste? (1-10)", 1, 10, 8)
    energia = st.select_slider("Nivel de energía", ["Baja", "Media", "Alta"])
    
    st.write("---")
    modo = st.radio("Actividad de hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (Partido 2h)"])
    meta_k = 3000.0 if modo == "Fútbol (Partido 2h)" else 2500.0
    
    # Hidratación (63kg)
    agua = ((63 * 35) / 1000) + (1.0 if modo == "Fútbol (Partido 2h)" else 0.5)
    st.info(f"💧 Agua hoy: **{agua:.2f} L**")
    
    st.divider()
    st.write(f"🔥 Meta: {st.session_state.k_t:.0f} / {meta_k:.0f} kcal")
    st.progress(min(st.session_state.k_t / meta_k, 1.0))

# --- 4. DASHBOARD ---
st.title(f"📈 {dias[hoy_idx]} de Xavier")

# Alerta Proteína
if datetime.now().hour >= 16 and st.session_state.p_t < 60:
    st.warning("🚨 ¡XAVIER! Falta proteína. ¡Busca huevos o pollo!")

t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    
    df_p = pd.DataFrame({'M':['Prot','Carb','Gras'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    fig = px
