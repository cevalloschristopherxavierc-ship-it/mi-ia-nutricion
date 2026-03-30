import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PERFIL DE USUARIO ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Activación de Núcleo Jarvis")
    with st.form("perfil_inicial"):
        st.write("Configura tus datos para el cálculo de macros:")
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Tu nombre?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 INICIAR SISTEMA"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. TIEMPO Y DÍAS ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy_nombre = dias_semana[hoy.weekday()]
hora_actual = hoy.hour

# --- 4. SIDEBAR (METAS COMPLETAS) ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    
    meta_k = 3200.0 if "Fútbol" in modo else 2700.0
    meta_p = st.session_state.u_pes * 2.2 
    meta_g = st.session_state.u_pes * 1.0 
    meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4 
    
    agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if "Fútbol" in modo else 0.6)
    
    st.success(f"📅 Hoy es: **{dia_hoy_nombre}**")
    st.info(f"💧 Agua: **{agua:.2f}L**")
    st.info(f"🍗 Prot: **{meta_p:.0f}g** | 🍚 Carb: **{meta_c:.0f}g** | 🥑 Gras: **{meta_g:.0f}g**")
    
    if st.button("🔄 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard Nutricional: {st.session_state.u_nom}")

# Lógica de Alarma de Proteína (Corregida la indentación)
p_actual = 0.0 
try:
    res_c = supabase.table('registros_comida').select('proteina').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res_c.data:
        p_actual = sum(float(r['prote
