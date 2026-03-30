import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. VERIFICACIÓN DE SEGURIDAD (ANTI-ERROR) ---
# Si faltan datos críticos, forzamos a que el perfil no esté listo
claves_necesarias = ['u_nom', 'u_pes', 'u_alt']
if not all(k in st.session_state for k in claves_necesarias):
    st.session_state.perfil_listo = False

# --- 3. PREGUNTAS DE INICIO ---
if not st.session_state.get('perfil_listo', False):
    st.title("🦾 Configuración de Jarvis")
    with st.form("perfil_inicial"):
        st.write("Completa tus datos para activar el núcleo:")
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Cómo te llamas?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Definición", "Fútbol"])
        
        if st.form_submit_button("🔥 ACTIVAR"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 4. LÓGICA DE TIEMPO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad:", ["Gym (Pierna/Glúteo)", "Fútbol (Partido 2h)"])
    meta_k = 3200.0 if modo == "Fútbol (Partido 2h)" else 2600.0
    agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if "Fútbol" in modo else 0.5)
    st.info(f"💧 Agua: **{agua:.2f}L**")
    
    if st.button("🔄 Cambiar Usuario"):
        st.session_state.clear()
        st.rerun()

# --- 6. DASHBOARD ---
st.title(f"📈 Dashboard: {st.session_state.u_nom}")
t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    try:
        res_h = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        if not df_h.empty:
            df_h['f'] = pd.to_datetime(df_h['created_at']).dt.date
            k_hoy = df_h[df_h['f'] == hoy.date()]['kcal'].sum()
            st.metric("Calorías Hoy", f"{k_hoy:.0f} / {meta_k:.0f}")
            st.progress(min(k_hoy/meta_k, 1.0))
        else: st.info("Sin registros esta semana.")
    except: pass

with t2:
    c_f, c_m = st.columns(2)
    res = None
    with c_f:
        foto = st.file_uploader("📸 Foto", type=["jpg","png"])
        if foto and st.button("🔍 ANALIZAR"):
            try:
                img = base64.b64encode(foto.read()).decode()
                p = "Responde solo: Nombre|Kcal|Prot|Carb|Gras"
                pld = {"contents":[{"parts":[{"text":p},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                r = requests.post(URL_AI, json=pld).json()
                d = r['candidates'][0]['content']['parts'][0]['text'].strip().replace(' ','').replace('g','').replace('*','').split('|')
                res = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
            except: st.error("Fallo IA")
    with c_m:
        with st.form("fm"):
            n_m = st.text_input("Comida")
            k_m = st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: res = {"n":n_m, "k":k_m, "p":0, "c":0, "g":0}
    if res:
        supabase.table('registros_comida').insert({
            "usuario": st
