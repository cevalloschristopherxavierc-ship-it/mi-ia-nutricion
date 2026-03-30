import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

# --- 2. CONEXIÓN ---
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
    .pizarra { background-color: #1e1e1e; border: 5px solid #59402a; border-radius: 12px; padding: 20px; color: white; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 20px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .verde { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    agente = st.text_input("Agente:", value="Xavier")
    meta = st.number_input("Meta Kcal:", value=2500)
    progreso = min(st.session_state.kcal_total / meta, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    if st.button("🔄 Reiniciar Día"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title("📈 Panel de Control")
t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        df_c = pd.DataFrame({'D': ['L','M','X','J','V','S','D'], 'K': [2530,2250,2310,2440,2630,2350,2500]})
        st.plotly_chart(px.bar(df_c, x='D', y='K', template="plotly_dark", color_discrete_sequence=['#FFC107']), use_container_width=True)
    with c_b:
        df_p = pd.DataFrame({'M': ['Ene','Feb','Mar','Abr','May','Jun','Jul'], 'Kg': [90,87,88,85,84,86,78]})
        st.plotly_chart(px.area(df_p, x='M', y='Kg', template="plotly_dark", color_discrete_sequence=['#00FF41']), use_container_width=True)

with t2:
    col_f, col_t = st.columns(2)
    comida = None

    with col_f:
        st.subheader("📸 Foto")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto:
            img_b64 = base64.b64encode(foto.read()).decode('utf-8')
            st.image(foto, width=200)
            if st.button("🔍 ESCANEAR"):
                with st.spinner("🤖 Analizando..."):
                    # LÍNEA 73 CORREGIDA Y PROTEGIDA:
                    instruccion = "Responde solo: Nombre|Kcal|Prot|Carb|Gras"
                    payload = {"contents": [{"parts": [{"text": instruccion}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
                    try:
                        r = requests.post(URL_AI, json=payload).json()
                        res = r['candidates'][0]['content']['parts'][0]['text'].split('|')
                        comida = {"n": res[0], "k": float(res[1]), "p": res[2], "c": res[3], "g": res[4]}
                    except:
                        st.error("Error en la conexión con la IA.")

    with col_t:
        st.subheader("✍️ Manual")
        with st.form("registro_manual"):
            m_n = st.text_input("Nombre del plato:")
            m_k = st.number_input("Calorías:", min_value=0.0)
            m_p = st.text_input("Proteína (g):", "0")
            if st.form_submit_button("REGISTRAR AHORA"):
                comida = {"n": m_n, "k": m_k, "p": m_p, "c": "0", "g": "0"}

    if comida:
        st.session_state.kcal_total += comida['k']
        try:
            supabase.table('registros_comida').insert({"usuario": agente, "comida": comida['n'], "kcal": comida['k'], "proteina": comida['p']}).execute()
            st.success("✅ Guardado en Supabase")
        except: pass
