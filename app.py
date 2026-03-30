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
    st.error("🚨 Error de Secrets. Verifica Supabase y Gemini.")
    st.stop()

# --- 2. PERFIL Y SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    with st.form("registro"):
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. TIEMPO Y RUTINA ---
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
    st.title(f"👑 Creador: {st.session_state.u_nom}")
    st.info(f"🏋️ **Hoy:** {rutina[dia_hoy]['ent']}")
    st.subheader("💧 Agua")
    ca1, ca2 = st.columns(2)
    if ca1.button("➕ 0.5L"): st.session_state.agua += 0.5; st.rerun()
    if ca2.button("🧹 Reset"): st.session_state.agua = 0.0; st.rerun()
    st.write(f"Total: **{st.session_state.agua}L**")
    st.subheader("👣 Pasos")
    st.session_state.pasos = st.number_input("Hoy:", 0, 50000, st.session_state.pasos, step=500)
    st.divider()
    st.subheader("🔐 Supervisor")
    cod = st.text_input("Código Maestro:", type="password")
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

# --- 6. DASHBOARD ---
st.title("📊 Panel Nutricional Xavier")
m1, m2, m3 = st.columns(3)
m1.metric("🔥 Calorías", f"{k_act:.0f}/{meta_k}")
m2.metric("🍗 Proteína", f"{p_act:.1f}g/{meta_p:.0f}g")
m3.metric("🏃 Quemado", f"{(st.session_state.pasos/1000)*38:.0f} kcal")

t1, t2, t3, t4 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 HORARIO", "🕵️ SUPERVISOR"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_b64 = base64.b64encode(foto.read()).decode()
                    payload = {"contents":[{"parts":[{"text":"Nombre|Kcal|Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=payload, timeout=15).json()
                    txt = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    pts = txt.split('|')
                    if len(pts) >= 3:
                        kv = float(re.findall(r"\d+", pts[1])[0])
                        pv = float(re.findall(r"\d+", pts[2])[0])
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":pts[0].strip(), "kcal":kv, "proteina":pv, "semana":inicio_sem}).execute()
                        st.rerun()
                except: st.error("Error IA. Intenta de nuevo.")
    with col_b:
        st.subheader("✍
