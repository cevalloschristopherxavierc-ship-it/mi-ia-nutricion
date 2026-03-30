import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis: Maestro Xavier", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("🚨 Error de Secrets. Verifica Supabase y Gemini.")
    st.stop()

# --- 2. PERFIL Y ESTADO ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    with st.form("registro"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = c1.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. LOGICA NUTRICIONAL ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
if 'h2o' not in st.session_state: st.session_state.h2o = 0.0
if 'steps' not in st.session_state: st.session_state.steps = 0

# Cálculos para Xavier (63kg)
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_g = st.session_state.u_pes * 0.9 
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4
meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if st.session_state.u_obj == "Fútbol" else 0.6)

# --- 4. SIDEBAR (METAS Y VIGILANCIA) ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.divider()
    
    # Barra de Agua (Línea 56 Corregida)
    st.subheader("💧 Hidratación")
    prog_agua = min(st.session_state.h2o / meta_agua, 1.0)
    st.progress(prog_agua)
    st.write(f"Llevas: **{st.session_state.h2o:.1f}L** / {meta_agua:.1f}L")
    if st.button("➕ Beber 500ml"): 
        st.session_state.h2o += 0.5
        st.rerun()
    
    st.divider()
    st.subheader("📊 Metas Diarias")
    st.info(f"🔥 Kcal: **{meta_k:.0f}**")
    st.info(f"🍗 Prot: **{meta_p:.0f}g**")
    
    st.divider()
    st.subheader("🕵️ Panel Maestro")
    target = st.text_input("Vigilar Discípulo:", placeholder="Nombre")
    btn_vigilar = st.button("👁️ Rastrear")

# --- 5. DASHBOARD PERSONAL ---
st.title(f"📊 Dashboard: {st.session_state.u_nom}")

# Obtener
