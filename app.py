import streamlit as st
import requests
import base64
import time
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
    st.error("⚠️ Error en Secrets. Revisa Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .pizarra { background-color: #1e1e1e; border: 5px solid #59402a; border-radius: 12px; padding: 20px; color: white; font-family: monospace; margin-bottom: 20px; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 20px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .verde { color: #00FF41; font-weight: bold; }
    .card-comida { background: #262626; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #00FF41; }
</style>
""", unsafe_allow_html=True)

# --- 4. SESIÓN DE DATOS (RECUERDO DE XAVIER) ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0
# Datos fijos de Xavier para evitar preguntas repetitivas
if 'user_data' not in st.session_state:
    st.session_state.user_data = {"nombre": "Xavier", "peso": 63.0, "altura": 170, "meta_p": 126.0}

# --- 5. SIDEBAR (PERFIL FIJO) ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    st.success(f"AGENTE: {st.session_state.user_data['nombre'].upper()}")
    
    # Permitir editar solo si es necesario, pero ya pre-cargado
    peso_act = st.number_input("Peso (kg):", value=st.session_state.user_data['peso'])
    meta_k = st.number_input("Meta Kcal:", value=2500)
    
    progreso = min(st.session_state.kcal_total / meta_k, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    
    if st.button("🔄 Reiniciar Día"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title("📈 Dashboard de Hipertrofia")
t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR COMIDA"])

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        df_c = pd.DataFrame({'D': ['L','M','X','J','V','S','D'], 'K': [2530,2250,2310,2440,2630,2350,2500]})
        st.plotly_chart(px.bar(df_c, x='D', y='K', title="Calorías Semanales", template="plotly_dark", color_discrete_sequence=['#FFC107']), use_container_width=True)
    with c_b:
        df_p = pd.DataFrame({'M': ['Ene','Feb','Mar','Abr','May','Jun','Jul'], 'Kg': [60,61,62,63,63,64,63]})
        st.plotly_chart(px.area(df_p, x='M', y='Kg', title="Evolución de Peso", template="plotly_dark", color_discrete_sequence=['#00FF41']), use_container_width=True)

with t2:
    col_f, col_t = st.columns(2)
    comida = None

    with col_f:
        st.subheader("📸 Escáner IA")
        foto = st.file_uploader("Sube tu plato", type=["jpg","png","jpeg"])
        if foto:
            img_b64 = base64.b64encode(foto.read()).decode('utf-8')
            st.image(foto, width=200)
            if st.button("🔍 ANALIZAR PLATO"):
                with st.spinner("🤖 Jarvis escaneando..."):
                    instruccion = "Responde solo: Nombre|Kcal|Prot|Carb|Gras"
                    payload = {"contents": [{"parts": [{"text": instruccion}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
                    try:
                        r = requests.post(URL_AI, json=payload).json()
                        res = r['candidates'][0]['content']['parts'][0]['text'].split('|')
                        comida = {"n": res[0], "k": float(res[1]), "p": res[2], "c": res[3], "g": res[4]}
                    except: st.error("Error IA")

    with col_t:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_entry"):
            m_n = st.text_input("¿Qué comiste?")
            m_k = st.number_input("Calorías:", min_value=0.0)
            m_p = st.text_input("Proteína (g
