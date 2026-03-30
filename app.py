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
    st.error("⚠️ Error de configuración. Revisa los Secrets.")
    st.stop()

# --- 2. PREGUNTAS DE INICIO (PERFIL) ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Bienvenido a Jarvis AI")
    with st.form("perfil_inicial"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Tu nombre?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Definición", "Fútbol"])
        if st.form_submit_button("🚀 INICIAR"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. LÓGICA SEMANAL ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"🦾 Perfil: {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    meta_k = 3000.0 if modo == "Fútbol (2h+)" else 2500.0
    
    agua = ((st.session_state.u_pes * 35) / 1000) + (1.0 if modo == "Fútbol (2h+)" else 0.5)
    st.info(f"💧 Agua: **{agua:.2f} L**")
    if st.button("🔄 Cambiar Usuario"):
        st.session_state.perfil_listo = False
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📈 {hoy.strftime('%A')} de {st.session_state.u_nom}")

t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    try:
        # Consulta filtrada por el nombre actual del usuario
        res_h = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        
        if not df_h.empty:
            k_hoy = df_h[pd.to_datetime(df_h['created_at']).dt.date == hoy.date()]['kcal'].sum()
            p_hoy = df_h[pd.to_datetime(df_h['created_at']).dt.date == hoy.date()]['proteina'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("Calorías Hoy", f"{k_hoy:.0f} / {meta_k:.0f}")
            c2.metric("Proteína Hoy", f"{p_hoy:.1f}g")
            st.progress(min(k_hoy/meta_k, 1.0))
        else:
            st.info("Aún no hay registros para este nombre en la semana actual.")
    except:
        st.warning("No hay datos previos.")

with t2:
    col_f, col_m = st.columns(2)
    res_final = None

    with col_f:
        st.subheader("
