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
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. GESTIÓN DE PERFIL (ANTI-ERRORES) ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Configuración de Jarvis")
    with st.form("perfil_inicial"):
        st.write("Ingresa tus datos para personalizar tu experiencia:")
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Cómo te llamas?", "Xavier")
        pes = c2.number_input("Peso actual (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Ganar Músculo", "Definición", "Fútbol"])
        
        if st.form_submit_button("🔥 ACTIVAR NÚCLEO"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. LÓGICA DE TIEMPO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# --- 4. SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad de hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    meta_k = 3200.0 if modo == "Fútbol (2h+)" else 2600.0
    # Cálculo de agua personalizado
    agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if "Fútbol" in modo else 0.5)
    st.info(f"💧 Agua diaria: **{agua:.2f}L**")
    
    if st.button("🔄 Cambiar Usuario"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard: {st.session_state.u_nom}")
t1, t2 = st.tabs(["📈 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    try:
        res_h = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        if not df_h.empty:
