import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# 1. SEGURIDAD Y CONEXIÓN
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error("⚠️ Configura los 'Secrets' en Streamlit Cloud (SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY).")
    st.stop()

# 2. ESTILOS VISUALES (PIZARRA Y DASHBOARD)
st.markdown("""
<style>
    .pizarra-contenedor { display: flex; justify-content: center; margin: 20px 0; }
    .pizarra-fondo {
        background-color: #262626; border: 8px solid #59402a; border-radius: 15px;
        padding: 25px; width: 100%; max-width: 450px; color: white; font-family: 'Courier New', monospace;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.5);
    }
    .pizarra-titulo { color: #00FF41; text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid #444; margin-bottom: 20px; }
    .pizarra-fila { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 18px; }
    .pizarra-valor { color: #00FF41; font-weight: bold; font-size: 20px; }
    .metric-card { background: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #333; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. ANIMACIÓN DE ENTRADA
if 'intro' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h1 style='text-align: center; color: #00FF41;'>🦾 JARVIS OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>SISTEMA DE BIOMETRÍA BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            bar.progress(i)
            time.sleep(0.01)
    placeholder.empty()
    st.session_state.intro = True

# 4. REGISTRO DE USUARIO
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>📋 REGISTRO DE PERFIL</h2>", unsafe_allow_html=True)
    with st.form("registro_pro"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre:")
            edad = st.number_input("Edad:", min_value=10, value=20)
        with col2:
            peso = st.number_input("Peso Actual (kg):", value=75.0)
            altura = st.number_input("Altura (cm):", value=170)
        
        if st.form_submit_button("INICIAR SESIÓN 🚀"):
            if nombre:
                m_p = peso * 2
                imc = round(peso / ((altura/100)**2), 1)
                u_data = {"nombre": nombre, "peso": peso, "altura": altura, "meta_p": m_p, "imc": imc}
                # Guardar en Supabase (opcional)
                try:
                    supabase.table('usuarios').insert({"nombre": nombre, "peso": peso, "altura": altura, "meta_proteina": m_p}).execute()
                except: pass
                st.session_state.usuario = u_data
                st.rerun()
            else:
                st.error("Por favor ingresa tu nombre.")
    st.stop()

# 5. PANEL DE CONTROL (DASHBOARD)
u = st.session_state.usuario

with st.sidebar:
    st.title("👤 PERFIL")
    st.success(f"AGENTE: {u['nombre'].upper()}")
    st.write(f"⚖️ Peso: {u['peso']}kg")
    st.write(f"📊 IMC: {u['imc']}")
    st.progress(0.8, text="Progreso Objetivo: 80%")
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

st.title("📈 Tu Progreso")

# Métricas rápidas
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="metric-card"><h2 style="color:#FFC107;">{u["peso"]} kg</h2><p>Actual</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card"><h2 style="color:#00FF41;">75.0 kg</h2><p>Objetivo</p></div>', unsafe_allow_html=True)

# Gráficas de estilo Pro (Simuladas con Plotly)
tab1, tab2 = st.tabs(["🔥 Calorías", "⚖️ Peso"])

with tab1:
    df_cal = pd.DataFrame({'Día': ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB', 'DOM'], 'Kcal': [2530, 2250, 2310, 2440, 2630, 2350, 2500]})
    fig1 = px.bar(df_cal, x='Día', y='Kcal', color_discrete_sequence=['#FFC107'], template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    df_peso = pd.DataFrame({'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'], 'Kg': [90, 87, 88, 85, 84, 86,
