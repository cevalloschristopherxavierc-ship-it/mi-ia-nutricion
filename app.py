import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

# --- 2. CONEXIÓN (SECRETS) ---
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Error en Secrets. Revisa Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS CSS (PIZARRA NEGRA) ---
st.markdown("""
<style>
    .pizarra { background-color: #1e1e1e; border: 5px solid #59402a; border-radius: 15px; padding: 20px; color: white; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 2px solid #333; margin-bottom: 15px; }
    .dato-p { display: flex; justify-content: space-between; font-size: 18px; margin: 5px 0; }
    .verde { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0

# --- 5. SIDEBAR (PROGRESO) ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    agente = st.text_input("Agente:", value="Xavier")
    meta = st.number_input("Meta Kcal Diaria:", value=2500)
    
    progreso = min(st.session_state.kcal_total / meta, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    
    if st.button("🔄 Reiniciar Día"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title("📈 Panel de Control")

tab1, tab2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔥 Calorías")
        df_cal = pd.DataFrame({'Día': ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB', 'DOM'], 'Kcal': [2530, 2250, 2310, 2440, 2630, 2350, 2500]})
        fig1 = px.bar(df_cal, x='Día', y='Kcal', template="plotly_dark", color_discrete_sequence=['#FFC107'])
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_b:
        st.subheader("⚖️ Historial de Peso")
        df_p = pd.DataFrame({'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'], 'Kg': [90, 87, 88, 85, 84, 86, 78]})
        fig2 = px.area(df_p, x='Mes', y='Kg', template="plotly_dark", color_discrete_sequence=['#00FF41'])
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    c_f, c_t = st.columns(2)
    comida = None

    with c_f:
        st.markdown("### 📸 Por Foto")
        foto = st.file_uploader("Sube tu plato", type=["jpg", "png", "jpeg"])
        if foto:
            img_b64 = base64.b64encode(foto.read()).decode('utf-8')
            st.image(foto, width=250)
            if st.button("🔍 ESCANEAR"):
