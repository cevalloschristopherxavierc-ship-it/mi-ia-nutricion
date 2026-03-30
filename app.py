import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PREGUNTAS DE INICIO (PERFIL DINÁMICO) ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Bienvenido a Jarvis AI")
    st.subheader("Configura tu perfil para empezar:")
    with st.form("perfil_inicial"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("¿Cómo te llamas?", "Usuario")
        peso = col2.number_input("Peso actual (kg)", 30.0, 200.0, 63.0)
        altura = col1.number_input("Altura (cm)", 100, 250, 170)
        objetivo = col2.selectbox("Tu objetivo", ["Ganar Músculo", "Perder Grasa", "Mantenerse"])
        
        if st.form_submit_button("🔥 ACTIVAR JARVIS"):
            st.session_state.u_nom = nombre
            st.session_state.u_peso = peso
            st.session_state.u_alt = altura
            st.session_state.u_obj = objetivo
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. LÓGICA DE SEMANA ACTUAL ---
hoy = datetime.now()
inicio_semana = hoy - timedelta(days=hoy.weekday()) # Lunes de esta semana
formato_semana = inicio_semana.strftime('%Y-%m-%d')

# --- 4. SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.title(f"🦾 Jarvis de {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_peso}kg | 📏 {st.session_state.u_alt}cm")
    
    st.divider()
    modo = st.radio("Actividad de hoy:", ["Gym (Hipertrofia)", "Fútbol / Cardio Intenso"])
    meta_k = 3000.0 if modo == "Fútbol / Cardio Intenso" else 2500.0
    
    # Hidratación personalizada
    agua = ((st.session_state.u_peso * 35) / 1000) + (1.0 if modo == "Fútbol / Cardio Intenso" else 0.5)
    st.info(f"💧 Agua diaria: **{agua:.2f} Litros**")
    
    if st.button("🗑️ Limpiar Historial"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard: {hoy.strftime('%A %d')}")

# Alerta de Proteína
if 'p_total' not in st.session_state: st.session_state.p_total = 0.0
if hoy.hour >= 16 and st.session_state.p_total < (st.session_state.u_peso * 1.5):
    st.warning("🚨 Alerta: Tu nivel de proteína es bajo para tus objetivos. ¡Prioriza snacks proteicos!")

t1, t2 = st.tabs(["📈 PROGRESO SEMANAL", "🍽️ REGISTRAR"])

with t1:
    # Aquí irían las métricas sumadas de la base de datos
    st.subheader(f"Resumen de la semana (Desde {formato_semana})")
    # Gráfica de macros profesional
    df_m = pd.DataFrame({'Macro':['Prot','Carb','Gras'], 'G':[20, 50, 30]}) # Ejemplo visual
    fig = px.pie(df_m, values='G', names='Macro', hole=0.6, template="plotly_dark", color_discrete_sequence=['#00FF41','#FFC107','#2196F3'])
    st.plotly_chart(fig, use_container_width=True)

with t2:
    c1, c2 = st.columns(2)
    res = None
    with c1:
        st.subheader("📸 Foto")
        foto = st.file_uploader("Escanear plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    prompt = "Responde SOLO: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    d = raw.replace(' ','').replace('g','').replace('*','').split('|')
                    res = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":
