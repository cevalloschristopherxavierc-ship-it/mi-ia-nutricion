import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# ==========================================
# 1. SEGURIDAD Y CONEXIÓN
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
        st.markdown("<h1 style='text-align: center; color: #00FF41;'>🦾 JARVIS OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
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
# 4. PREGUNTAS DE INICIO (OBLIGATORIAS)
# ==========================================
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Si no hay usuario en sesión, mostrar SOLO el formulario
if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>📝 REGISTRO DE AGENTE</h2>", unsafe_allow_html=True)
    with st.form("registro_obligatorio"):
        nombre = st.text_input("¿Cuál es tu nombre?")
        peso = st.number_input("¿Cuál es tu peso (kg)?", min_value=30.0, value=63.0)
        enviar = st.form_submit_button("ACTIVAR SISTEMA 🚀")
        
        if enviar:
            if nombre:
                meta_p = peso * 2
                # Guardar en base de datos
                try:
                    supabase.table('usuarios').insert({"nombre": nombre, "peso": peso, "meta_proteina": meta_p}).execute()
                except: pass
                
                st.session_state.usuario = {"nombre": nombre, "peso": peso, "meta": meta_p}
                st.rerun() # Aquí usamos el rerun que mencionaste para refrescar
            else:
                st.error("⚠️ El nombre es obligatorio.")
    st.stop() # DETIENE TODO AQUÍ hasta que se registren

# ==========================================
# 5. INTERFAZ TRAS EL REGISTRO (ESCÁNER)
# ==========================================
u = st.session_state.usuario

with st.sidebar:
    st.title("📂 SESIÓN")
    st.success(f"AGENTE: {u['nombre'].upper()}")
    st.write(f"⚖️ Peso: {u['peso']}kg")
    st.write(f"🍗 Meta: {u['meta']}g Prot")
    
    # MODO CREADOR XAVIER
    if "xavier" in u['nombre'].lower():
        st.divider()
        st.markdown("### 👑 MODO CREADOR")
        if st.button("📊 VER USUARIOS"):
