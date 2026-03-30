import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# ==========================================
# 1. SEGURIDAD Y CONEXIÓN (SECRETS)
# ==========================================
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# ==========================================
# 2. ANIMACIÓN DE CARGA (XAVIER CEVALLOS)
# ==========================================
if 'intro' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h1 style='text-align: center; color: #00FF41; font-family: monospace;'>🦾 JARVIS OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>SISTEMA DE BIOMETRÍA BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            bar.progress(i)
            time.sleep(0.01)
    placeholder.empty()
    st.session_state.intro = True

# ==========================================
# 3. ESTILOS (PIZARRA PROFESIONAL)
# ==========================================
st.markdown("""
<style>
    .pizarra { background-color: #121212; border: 5px solid #3d2b1f; border-radius: 15px; padding: 25px; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-size: 22px; border-bottom: 2px solid #333; margin-bottom: 15px; }
    .dato { display: flex; justify-content: space-between; font-size: 19px; margin: 10px 0; color: #fff; }
    .val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. REGISTRO COMPLETO (PREGUNTAS)
# ==========================================
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Si no hay usuario, mostrar FORMULARIO DE REGISTRO
if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>📋 REGISTRO DE PERFIL</h2>", unsafe_allow_html=True)
    with st.form("registro_completo"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre:")
            edad = st.number_input("Edad:", min_value=10, max_value=100, value=20)
        with col2:
            peso = st.number_input("Peso (kg):", min_value=30.0, value=63.0)
            altura = st.number_input("Altura (cm):", min_value=100, max_value=250, value=170)
        
        enviar = st.form_submit_button("SINCRONIZAR CON JARVIS 🚀")
        
        if enviar:
            if nombre:
                # Cálculos
                meta_p = peso * 2
                imc = round(peso / ((altura/100)**2), 1
