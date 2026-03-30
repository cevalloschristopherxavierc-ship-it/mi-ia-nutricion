import streamlit as st
import requests
import base64
import pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis: Maestro Xavier", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("🚨 Error de Secrets. Verifica Supabase y Gemini.")
    st.stop()

# --- 2. PERFIL Y SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    with st.form("registro_inicial"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso Actual (kg):", 30.0, 150.0, 63.0)
        obj = c1.selectbox("Objetivo Principal:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER AL SISTEMA"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.session_state.h2o = 0.0 # Inicializar Agua
            st.rerun()
    st.stop()

# --- 3. TIEMPO Y METAS ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = dias[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# Lógica de Metas basada en 63kg y Fútbol
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 # ~138g
meta_g = (meta_k * 0.25) / 9 # Grasas al 25% (salud hormonal)
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. SIDEBAR (Agua, Pasos y Creador) ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.subheader(f"📅 {dia_hoy}")
    
    st.divider()
    # Contador de Agua (Restauration)
    st.subheader("💧 Control Hidratación")
    c_h1, c_h2 = st.columns(2)
    if c_h1.button("➕ 500ml"): 
        st.session_state.h2o += 0.5
    if c_h2.button("🧹 Limpiar"): 
        st.session_state.h2o = 0.0
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Consumo Agua: **{st.session_state.h2o}L** / 3.5L")

    st.divider()
    # Contador de Pasos (Novedad)
    st.subheader("👣 Actividad Diaria")
    steps = st.number_input("Pasos hoy:", 0, 50000, 0, 500)
    kcal_steps = (steps / 1000) * 38 # Estimación quemada
    st.metric("Quemado Pasos", f"{kcal_steps:.0f} Kcal")

    st.divider()
    # Creador Protegido
    st.subheader("🔐 Supervisor")
    cod = st.text_input("Código Maestro:", type="password")
    st.session_state.creador = (cod == "xavier2210")

# --- 5. OBTENCIÓN DE DATOS DE HOY ---
p_act, k_act, c_act, g_act = 0.0, 0.0, 0.0, 0.0
df_hoy = pd.DataFrame()
df_all = pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[df_all['fecha'] == hoy.date()]
        if not df_hoy.empty:
            k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
            # Estimación de Carbos/Grasas basada en Kcal restantes
            c_act = (k_act * 0.5) / 4 if k_act > 0 else
