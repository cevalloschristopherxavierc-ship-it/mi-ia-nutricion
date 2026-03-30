import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

# --- 2. CONEXIÓN ---
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .pizarra { background-color: #1e1e1e; border: 5px solid #59402a; border-radius: 12px; padding: 20px; color: white; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 20px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .verde { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    agente = st.text_input("Agente:", value="Xavier")
    meta = st.number_input("Meta Kcal:", value=2500)
    progreso = min(st.session_state.kcal_total / meta, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    if st.button("🔄 Reiniciar"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title("📈 Panel de Control")
t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        df_c = pd.DataFrame({'D': ['L','M','X','J','V','S','D'], 'K': [2530,2250,2310,2440,2630,2350,2500]})
        st.plotly_chart(px.bar(df_c, x='D', y='K', template="plotly_dark", color_discrete_sequence=['#FFC107']), use_container_width=True)
    with c_b:
        df_p = pd.DataFrame({'M': ['Ene','Feb','Mar','Abr','May','Jun','Jul'], 'Kg': [90,87,88,85,84,86,78]})
        st.plotly_chart(px.area(df_p, x='M', y='Kg', template="plotly_dark", color_discrete_sequence=['#00FF41']), use_container_width=True)

with t2:
    col_f, col_t = st.columns(2)
    comida = None

    with col_f:
        st.subheader("📸 Foto")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto:
            img_b64 = base64.b64encode(foto.read()).decode('utf-8')
            st.image(foto, width=200)
            # LÍNEA 79 CORREGIDA (BLOQUE INDENTADO):
            if st.button("🔍 ESCANEAR"):
                with st.spinner("🤖 Analizando..."):
                    payload = {"contents": [{"parts": [{"text": "Responde:
