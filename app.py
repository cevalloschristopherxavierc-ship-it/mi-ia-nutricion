import streamlit as st
import requests
import base64
import pandas as pd
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
    st.error("🚨 Revisa los Secrets en Streamlit.")
    st.stop()

# --- 2. SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Activación Jarvis")
    with st.form("reg"):
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ENTRAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. RUTINA Y METAS ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = dias[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

rutina = {
    "Lunes": {"ent": "🍗 Piernas/Glúteo (Fuerza)", "com": "🍳 Huevos/Avena | 🍗 Pollo/Arroz"},
    "Martes": {"ent": "👕 Pecho/Tríceps/Hombro", "com": "🥤 Batido/Banano | 🥩 Carne/Pasta"},
    "Miércoles": {"ent": "🔙 Espalda/Bíceps", "com": "🍳 Claras/Pan | 🦃 Pavo/Arroz"},
    "Jueves": {"ent": "🍗 Piernas/Glúteo (Hipertrofia)", "com": "🥣 Yogur/Nueces | 🍗 Pollo/Lentejas"},
    "Viernes": {"ent": "⚽ Fútbol (Partido)", "com": "🥣 Avena/Fruta | 🍝 Pasta/Pollo"},
    "Sábado": {"ent": "💪 Torso Superior", "com": "🥞 Pancakes Avena | 🐟 Pescado/Papa"},
    "Domingo": {"ent": "🛌 Descanso", "com": "🥗 Ensalada y Proteína"}
}

meta_k = 3200 if st.session_state.u_obj == "Fútbol" else 2750
meta_p = st.session_state.u_pes * 2.2 
if 'agua' not in st.session_state: st.session_state.agua = 0.0
if 'pasos' not in st.session_state: st.session_state.pasos = 0

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.info(f"🏋️ {rutina[dia_hoy]['ent']}")
    st.subheader("💧 Agua")
    c1, c2 = st.columns(2)
    if c1.button("➕ 0.5L"): st.session_state.agua += 0.5; st.rerun()
    if c2.button("🧹 Reset"): st.session_state.agua = 0.0; st.rerun()
    st.write(f"Total: **{st.session_state.agua}L**")
    st.session_state.pasos = st.number_input("👣 Pasos:", 0, 50000, st.session_state.pasos, 500)
    st.divider()
    cod = st.text_input("🔐 Código Maestro:", type="password")
    st.session_state.creador = (cod == "xavier2210")

# --- 5. DATA ---
p_act, k_act = 0.0, 0.0
df_hoy, df_all = pd.DataFrame(), pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', inicio_sem).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[(df_all['usuario'] == st.session_state.u_nom) & (df_all['fecha'] == hoy.date())]
        k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
except: pass

# --- 6. UI ---
st.title("📊 Panel Xavier")
col1, col2, col3 = st.columns(3)
col1.metric("🔥 Kcal", f"{k_act:.0f}/{meta_k}")
col2.metric("🍗 Prot", f"{p_act:.1f}g/{meta_p:.0f}g")
col3.metric("🏃 Pasos", f"{(st.session_state.pasos/1000)*38:.0f} kcal")

t1, t2, t3, t4 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 DIARIO", "🕵️ CREADOR"])

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("S
