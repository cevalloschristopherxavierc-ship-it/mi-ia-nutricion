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
except Exception as e:
    st.error("⚠️ Error en Secrets. Revisa Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS (PIZARRA Y CARDS) ---
st.markdown("""
<style>
    .pizarra { background-color: #1a1a1a; border: 4px solid #59402a; border-radius: 15px; padding: 20px; color: white; font-family: 'Courier New', monospace; margin: 10px 0; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 1px solid #333; margin-bottom: 15px; text-transform: uppercase; }
    .verde { color: #00FF41; font-weight: bold; }
    .card-comida { background: #262626; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 6px solid #00FF41; box-shadow: 2px 2px 10px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

# --- 4. MEMORIA DE XAVIER (170cm / 63kg) ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nombre": "Xavier",
        "peso": 63.0,
        "altura": 170,
        "objetivo": "Hipertrofia Glúteos/Piernas"
    }

# --- 5. SIDEBAR (PERFIL Y METAS) ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    st.success(f"AGENTE: {st.session_state.user_profile['nombre'].upper()}")
    st.info(f"📍 Portoviejo | 📏 {st.session_state.user_profile['altura']} cm")
    
    peso_v = st.number_input("Peso Actual (kg):", value=st.session_state.user_profile['peso'], step=0.1)
    meta_k = st.number_input("Meta Kcal Diaria:", value=2500)
    
    # Barra de progreso dinámica
    progreso = min(st.session_state.kcal_total / meta_k, 1.0)
    st.write(f"🔥 Progreso Hoy: {int(progreso * 100)}%")
    st.progress(progreso)
    st.write(f"Consumido: {int(st.session_state.kcal_total)} / {meta_k} kcal")
    
    if st.button("🔄 Reiniciar Contador"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title("📈 Dashboard Nutricional")
t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR COMIDA"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        df_c = pd.DataFrame({'D': ['L','M','X','J','V','S','D'], 'K': [2530,2250,2310,2440,2630,2350,2500]})
        st.plotly_chart(px.bar(df_c, x='D', y='K', title="Calorías de la Semana", template="plotly_dark", color_discrete_sequence=['#FFC107']), use_container_width=True)
    with col_b:
        # Gráfica con tus datos reales de peso
        df_p = pd.DataFrame({'M': ['Ene','Feb','Mar','Abr','May','Jun','Jul'], 'Kg': [60,61,62,63,63,64,63]})
        st.plotly_chart(px.area(df_p, x='M', y='Kg', title="Evolución de Masa Corporal", template="plotly_dark", color_discrete_sequence=['#00FF41']), use_container_width=True)

with t2:
    col_foto, col_texto = st.columns(2)
    comida_final = None

    with col_foto:
        st.subheader("📸 Escáner IA")
        foto = st.file_uploader("Sube foto de tu plato", type=["jpg","png","jpeg"], key="camara_x")
        if foto:
            img_b64 = base64.b64encode(foto.read()).decode('utf-8')
            st.image(foto, width=220)
            if st.button("🔍 ANALIZAR PLATO"):
                with st.spinner("🤖 Jarvis analizando biometría..."):
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "Responde estrictamente en este formato: Nombre|Kcal|Prot|Carb|Gras"},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                            ]
                        }]
                    }
                    try:
                        r = requests.post(URL_AI, json=payload).json()
                        res = r['candidates'][0]['content']['parts'][0]['text'].strip().split('|')
                        # Limpieza de datos para asegurar números
                        comida_final = {
                            "n": res[0], 
                            "k": float(res[1].replace('kcal','')), 
                            "p": float(res[2].replace('g','')), 
                            "c": res[3], "g": res[4]
                        }
                    except: st.error("❌ Error en el análisis. Intenta otra vez.")

    with col_texto:
        st.subheader("✍️ Registro Manual")
        with st.form("form_manual_x"):
            m_n = st.text_input("Nombre de la comida:")
            m_
