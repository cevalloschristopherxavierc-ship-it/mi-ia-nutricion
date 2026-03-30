import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Nutrición Pro", layout="wide")

# --- 2. CONEXIÓN (SECRETS) ---
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .pizarra { background-color: #1a1a1a; border: 4px solid #59402a; border-radius: 15px; padding: 20px; color: white; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .verde { color: #00FF41; font-weight: bold; }
    .macro-box { text-align: center; background: #262626; padding: 10px; border-radius: 10px; border: 1px solid #444; width: 22%; }
</style>
""", unsafe_allow_html=True)

# --- 4. INICIALIZAR SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0
if 'prot' not in st.session_state: st.session_state.prot = 0.0
if 'carb' not in st.session_state: st.session_state.carb = 0.0
if 'gras' not in st.session_state: st.session_state.gras = 0.0

# --- 5. SIDEBAR: PREGUNTAS PARA USUARIOS ---
with st.sidebar:
    st.title("🦾 PERFIL JARVIS")
    st.info("Configura tu perfil de atleta:")
    u_nom = st.text_input("Nombre:", value="Xavier")
    u_pes = st.number_input("Peso Actual (kg):", value=63.0, help="Si eres nuevo, ajusta tu peso aquí.")
    u_alt = st.number_input("Estatura (cm):", value=170)
    u_eda = st.number_input("Edad:", value=20)
    
    meta_diaria = st.number_input("Meta Kcal Diaria:", value=2500)
    
    st.divider()
    prog = min(st.session_state.kcal_total / meta_diaria, 1.0)
    st.write(f"🔥 Progreso: {int(prog * 100)}%")
    st.progress(prog)
    st.write(f"Consumido: {int(st.session_state.kcal_total)} / {int(meta_diaria)} kcal")
    
    if st.button("🔄 Reiniciar Día"):
        st.session_state.kcal_total = 0.0
        st.session_state.prot = 0.0
        st.session_state.carb = 0.0
        st.session_state.gras = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title(f"📈 Dashboard Nutricional: {u_nom}")
t1, t2 = st.tabs(["📊 MI PROGRESO", "🍽️ REGISTRAR COMIDA"])

with t1:
    m1, m2, m3 = st.columns(3)
    m1.metric("Proteína Total", f"{st.session_state.prot} g")
    m2.metric("Carbohidratos Total", f"{st.session_state.carb} g")
    m3.metric("Grasas Total", f"{st.session_state.gras} g")
    
    df_macros = pd.DataFrame({
        'Nutriente': ['Proteína', 'Carbos', 'Grasas'],
        'Gramos': [st.session_state.prot, st.session_state.carb, st.session_state.gras]
    })
    st.plotly_chart(px.pie(df_macros, values='Gramos', names='Nutriente', hole=0.5, template="plotly_dark", 
                          color_discrete_sequence=['#00FF41', '#FFC107', '#2196
