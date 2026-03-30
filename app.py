import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# 1. SEGURIDAD
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# 2. ANIMACIÓN DE CARGA
if 'intro' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h1 style='text-align: center; color: #00FF41;'>🦾 JARVIS OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>SISTEMA BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            bar.progress(i)
            time.sleep(0.01)
    placeholder.empty()
    st.session_state.intro = True

# 3. ESTILOS
st.markdown("""
<style>
    .pizarra { background-color: #121212; border: 4px solid #3d2b1f; border-radius: 12px; padding: 20px; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-size: 20px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .dato { display: flex; justify-content: space-between; font-size: 18px; margin: 8px 0; color: #fff; }
    .val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 4. REGISTRO (PREGUNTAS)
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>📋 REGISTRO INICIAL</h2>", unsafe_allow_html=True)
    with st.form("registro_final"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre:")
            edad = st.number_input("Edad:", min_value=10, max_value=100, value=20)
        with c2:
            peso = st.number_input("Peso (kg):", min_value=30.0, value=63.0)
            altura = st.number_input("Altura (cm):", min_value=100, max_value=250, value=170)
        
        if st.form_submit_button("ACTIVAR JARVIS 🚀"):
            if nombre:
                m_p = peso * 2
                imc = round(peso / ((altura/100)**2), 1)
                u_data = {"nombre": nombre, "peso": peso, "altura": altura, "edad": edad, "meta_p": m_p, "imc": imc}
                try:
                    supabase.table('usuarios').insert({"nombre": nombre, "peso": peso, "altura": altura, "edad": edad, "meta_proteina": m_p}).execute()
                except: pass
                st.session_state.usuario = u_data
                st.rerun()
            else:
                st.error("⚠️ El nombre es necesario.")
    st.stop()

# 5. INTERFAZ PRINCIPAL
u = st.session_state.usuario
with st.sidebar:
    st.title("📂 BIOMETRÍA")
    st.success(f"AGENTE: {u.get('nombre', '').upper()}")
    st.write(f"⚖️ Peso: {u.get('peso')}kg | 📏 Altura: {u.get('altura')}cm")
    st.write(f"📊 IMC: {u.get('imc')}")
    st.divider()
    st.write(f"🎯 Meta Proteína: {u.get('meta_p', 0)}g")
    
    if "xavier" in u.get('nombre', '').lower():
        st.divider()
        st.markdown("### 👑 MODO CREADOR")
        if st.button("📊 VER USUARIOS"):
            res = supabase.table('usuarios').select('*').execute()
            st.dataframe(res.data)
            
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

st.subheader("📸 ESCÁNER NUTRICIONAL")
foto = st.file_uploader("Sube tu comida", type=["jpg", "png", "jpeg"])

if foto:
    img_64 = base6
