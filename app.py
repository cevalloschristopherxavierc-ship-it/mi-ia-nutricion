import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client
import re

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Jarvis: Maestro Xavier", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("🚨 Error de conexión. Revisa tus Secrets en Streamlit.")
    st.stop()

# --- 2. PERFIL DEL MAESTRO ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Activación de Jarvis")
    with st.form("registro"):
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso Actual (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo Principal:", ["Hipertrofia (Pierna/Glúteo)", "Fútbol / Rendimiento", "Definición"])
        if st.form_submit_button("🚀 INICIAR SISTEMA"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom, pes, obj
            st.rerun()
    st.stop()

# --- 3. VARIABLES DE ESTADO (Agua y Pasos) ---
if 'agua' not in st.session_state: st.session_state.agua = 0.0
if 'pasos' not in st.session_state: st.session_state.pasos = 0

# --- 4. LÓGICA DE ENTRENAMIENTO Y METAS ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = dias[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# Tu rutina real
rutina = {
    "Lunes": "🍗 Piernas y Glúteos (Fuerza)",
    "Martes": "👕 Pecho, Tríceps y Hombros",
    "Miércoles": "🔙 Espalda y Bíceps",
    "Jueves": "🍗 Piernas y Glúteos (Hipertrofia)",
    "Viernes": "⚽ Fútbol (Día de Partido / Cardio)",
    "Sábado": "💪 Torso Superior (Pecho/Espalda)",
    "Domingo": "🛌 Descanso Total"
}

# Metas calculadas para Xavier (63kg)
meta_kcal = 3200 if "Fútbol" in st.session_state.u_obj else 2750
meta_prot = st.session_state.u_pes * 2.2 # ~138g
kcal_pasos = (st.session_state.pasos / 1000) * 38

# --- 5. SIDEBAR (Control Rápido) ---
with st.sidebar:
    st.title(f"👤 {st.session_state.u_nom}")
    st.info(f"📅 **Hoy:** {dia_hoy}\n\n🏋️ **Entreno:** {rutina[dia_hoy]}")
    st.divider()
    st.subheader("💧 Control de Agua")
    col_h1, col_h2 = st.columns(2)
    if col_h1.button("➕ 500ml"): st.session_state.agua += 0.5
    if col_h2.button("🧹 Limpiar"): st.session_state.agua = 0.0
    st.write(f"Consumo: **{st.session_state.agua}L**")
    
    st.subheader("👣 Actividad")
    st.session_state.pasos = st.number_input("Pasos de hoy:", 0, 50000, st.session_state.pasos, step=500)
    if st.button("🔄 Reiniciar Todo"):
        st.session_state.clear()
        st.rerun()

# --- 6. DASHBOARD PRINCIPAL ---
st.title("📊 Panel de Control Nutricional")

# Obtener datos de Supabase
p_act, k_act = 0.0, 0.0
df_hoy = pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[df_all['fecha'] == hoy.date()]
        k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
except: pass

# Métricas Visuales
c1, c2, c3 = st.columns(3)
c1.metric("🔥 Calorías", f"{k_act:.0f} / {meta_kcal}")
c2.metric("🍗 Proteína", f"{p_act:.1f}g / {meta_prot:.0f}g")
c3.metric("🏃 Quemado (Pasos)", f"{kcal_pasos:.0f} kcal")

t1, t2, t3 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 HORARIO Y DIARIO"])

with t1:
    col_a, col_b = st.columns(2)
