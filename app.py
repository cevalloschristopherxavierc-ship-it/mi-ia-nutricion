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

# --- 2. PERFIL Y SESIÓN (REGISTRO OBLIGATORIO) ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    st.info("Configura tu perfil para empezar el rastreo en Portoviejo.")
    with st.form("registro_inicial"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = c1.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER AL DASHBOARD"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_obj = obj
            st.rerun()
    st.stop()

# --- 3. LÓGICA NUTRICIONAL Y PASOS ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# Inicializar variables de estado si no existen
if 'h2o' not in st.session_state: st.session_state.h2o = 0.0
if 'steps' not in st.session_state: st.session_state.steps = 0

obj_act = st.session_state.get('u_obj', "Hipertrofia")
meta_k = 3200.0 if obj_act == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if obj_act == "Fútbol" else 0.6)

# Cálculo de quema por pasos (Aprox 38 kcal por cada 1000 pasos para 63kg)
kcal_pasos = (st.session_state.steps / 1000) * 38

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.divider()
    
    st.subheader("👣 Actividad Diaria")
    # El número de pasos se actualiza aquí y afecta las métricas al instante
    st.session_state.steps = st.number_input("Registrar Pasos:", 0, 50000, st.session_state.steps, step=500)
    st.write(f"🔥 Quemado: **{kcal_pasos:.0f} kcal**")
    
    st.divider()
    st.subheader("💧 Hidratación")
    prog_agua = min(st.session_state.h2o / meta_agua, 1.0)
    st.progress(prog_agua)
    st.write(f"**{st.session_state.h2o:.1f}L** / {meta_agua:.1f}L")
    if st.button("➕ Beber 500ml"): 
        st.session_state.h2o += 0.5
        st.rerun()
    
    st.divider()
    if st.button("🔄 Cerrar Sesión / Reiniciar"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD PRINCIPAL ---
st.title(f"📊 Dashboard: {st.session_state.u_nom}")

# Carga de datos de Supabase
p_act, k_act = 0.0, 0.0
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.date
        hoy_df = df[df['f'] == hoy.date()]
        k_act, p_act = hoy_df['kcal'].sum(), hoy_df['proteina'].sum()
except:
    pass

# Métricas de Balance
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kcal Consumidas", f"{k_act:.0f}", f"Meta: {meta_k:.0f}")
m2.metric("Proteína", f"{p_act:.1f}g", f"Meta: {meta_p:.0f}g")
m3.metric("Gasto por Pasos", f"{kcal_pasos:.0f} kcal")
m4.metric("Balance Neto", f"{(k_act - kcal_pasos):.0f} kcal")

t1, t2 = st.tabs(["📈 ANÁLISIS", "🍽️ REGISTRO"])

with t1:
    if k_act > 0:
        fig = px.pie(values=[p_act*4, abs(k_act-(p_act*4)-400), 400], names=['Prot', 'Carb', 'Gras'], hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra comida para ver macros.")

with t2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📸 Foto IA")
        foto
