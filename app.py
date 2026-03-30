import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# ==========================================
# 1. SEGURIDAD (CONEXIÓN NUBE)
# ==========================================
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ ERROR: Configura los Secrets en Streamlit Cloud.")
    st.stop()

# ==========================================
# 2. ANIMACIÓN DE CARGA (XAVIER CEVALLOS)
# ==========================================
if 'intro_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"<h1 style='text-align: center; color: #00FF41; font-family: monospace;'>🦾 JARVIS SYSTEM</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #888;'>DESARROLLADO POR: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            bar.progress(i)
            time.sleep(0.01)
        st.success("✅ SISTEMA CARGADO")
        time.sleep(0.8)
    placeholder.empty()
    st.session_state.intro_done = True

# ==========================================
# 3. ESTILO VISUAL (PIZARRA NEGRA)
# ==========================================
st.markdown("""
<style>
    .pizarra { background-color: #121212; border: 5px solid #3d2b1f; border-radius: 15px; padding: 25px; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-size: 22px; border-bottom: 2px solid #333; padding-bottom: 10px; }
    .dato { display: flex; justify-content: space-between; font-size: 19px; margin: 10px 0; color: #fff; }
    .val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LAS PREGUNTAS DEL INICIO (REGISTRO)
# ==========================================
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Si no hay usuario, MOSTRAR PREGUNTAS
if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>📝 REGISTRO DE AGENTE</h2>", unsafe_allow_html=True)
    with st.form("preguntas_inicio"):
        nombre = st.text_input("¿Cuál es tu nombre?")
        peso = st.number_input("¿Cuál es tu peso actual (kg)?", min_value=30.0, value=63.0)
        
        btn_activar = st.form_submit_button("ACTIVAR JARVIS 🚀")
        
        if btn_activar:
            if nombre:
                # Calculamos meta de proteína (Peso x 2)
                meta = peso * 2
                # Guardamos en la base de datos
                try:
                    supabase.table('usuarios').insert({"nombre": nombre, "peso": peso, "meta_proteina": meta}).execute()
                except: pass
                
                # Guardamos en la sesión
                st.session_state.usuario = {"nombre": nombre, "peso": peso, "meta": meta}
                st.rerun
