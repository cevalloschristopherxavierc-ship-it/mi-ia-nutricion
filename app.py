import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN DE SISTEMA ---
st.set_page_config(page_title="Jarvis OS | Xavier", layout="wide", page_icon="🦾")

# CSS para un look profesional "Dark Mode" de alto contraste
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stProgress > div > div > div > div { background-color: #4facfe; }
    </style>
    """, unsafe_url_as_supported=True)

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        st.error("🚨 Error de enlace con la base de datos.")
        st.stop()

supabase = init_connection()

# --- 2. GESTIÓN DE SESIÓN Y PERFIL ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Inicializando Protocolo Jarvis")
    with st.form("perfil_maestro"):
        c1, c2, c3 = st.columns(3)
        nom = c1.text_input("Identificación:", "Xavier")
        pes = c2.number_input("Peso Base (kg):", 30.0, 150.0, 63.0)
        obj = c3.selectbox("Misión:", ["Fútbol", "Hipertrofia", "Definición"])
        if st.form_submit_button("🚀 ACTIVAR SISTEMA"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.session_state.h2o = 0.0
            st.rerun()
    st.stop()

# --- 3. ALGORITMO DE METAS (Portoviejo Elite) ---
hoy = datetime.now()
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# Metas calculadas para Xavier (63kg)
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2  # 138.6g Prot
meta_g = (meta_k * 0.25) / 9           # ~89g Grasa
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4 # El resto en Carb

# --- 4. INTERFAZ LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title(f"👑 Maestro {st.session_state.u_nom}")
    st.subheader(f"📅 {hoy.strftime('%A, %d %B')}")
    st.divider()
    
    # Módulo de Hidratación Profesional
    st.subheader("💧 Registro de Hidratación")
    prog_h2o = min(st.session_state.h2o / 3.5, 1.0)
    st.progress(prog_h2o)
    st.write(f"Nivel actual: **{st.session_state.h2o:.1f}L** de 3.5L")
    ch1, ch2 = st.columns(2)
    if ch1.button("➕ 500ml"): st.session_state.h2o += 0.5; st.rerun()
    if ch2.button("🧹 Reset"): st.session_state.h2o = 0.0; st.rerun()
    
    st.divider()
    # Módulo de Actividad
    st.subheader("👣 Sensor de Pasos")
    pasos = st.number_input("Pasos registrados:", 0, 50000, 0, 500)
    kcal_p = (pasos / 1000) * 38
    st.metric("Gasto Actividad", f"{kcal_p:.0f} Kcal")
    
    st.divider()
    # Acceso Creador
    key = st.text_input("🔐 Acceso Creador:", type="password")
    st.session_state.creador = (key == "xavier2210")

# --- 5. MOTOR DE DATOS ---
k_act, p_act, g_act, c_act = 0.0, 0.0, 0.0, 0.0
df_hoy, df_all = pd.DataFrame(), pd.DataFrame()
try:
    data = supabase.table('registros_comida').select('*').eq('semana', ini_s).execute()
    if data.data:
        df_all = pd.DataFrame(data.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[(df_all['usuario'] == st.session_state.u_nom) & (df_all['fecha'] == hoy.date())]
        if not df_hoy.empty:
            k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
            g_act = (k_act * 0.25) / 9
            c_act
