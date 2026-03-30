import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Nutrición Pro", layout="wide")

# --- 2. CONEXIÓN ---
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .pizarra { background-color: #1a1a1a; border: 4px solid #59402a; border-radius: 15px; padding: 20px; color: white; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .verde { color: #00FF41; font-weight: bold; }
    .macro { text-align: center; padding: 10px; background: #262626; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 4. MEMORIA DE SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0
if 'macros' not in st.session_state: st.session_state.macros = {"p": 0.0, "c": 0.0, "g": 0.0}

# --- 5. SIDEBAR: PREGUNTAS PARA USUARIO NUEVO ---
with st.sidebar:
    st.title("🦾 CONFIGURACIÓN JARVIS")
    st.info("Introduce tus datos para calcular tu plan:")
    
    nombre = st.text_input("Tu Nombre:", value="Xavier")
    peso = st.number_input("Peso Actual (kg):", min_value=30.0, value=63.0, step=0.1)
    estatura = st.number_input("Estatura (cm):", min_value=100, value=170)
    edad = st.number_input("Edad:", min_value=10, value=20)
    genero = st.selectbox("Género:", ["Masculino", "Femenino"])
    
    # Cálculo automático de Meta Base (Harris-Benedict simplificado)
    if genero == "Masculino":
        tmb = 88.36 + (13.4 * peso) + (4.8 * estatura) - (5.7 * edad)
    else:
        tmb = 447.59 + (9.2 * peso) + (3.1 * estatura) - (4.3 * edad)
    
    meta_cal = st.number_input("Ajustar Meta Diaria (kcal):", value=int(tmb * 1.5)) # Factor actividad moderada
    
    st.divider()
    progreso = min(st.session_state.kcal_total / meta_cal, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    st.write(f"Consumido: {int(st.session_state.kcal_total)} / {int(meta_cal)} kcal")

# --- 6. PANEL PRINCIPAL ---
st.title(f"📈 Panel de Control: {nombre}")
t1, t2 = st.tabs(["📊 MI PROGRESO", "🍽️ REGISTRAR ALIMENTO"])

with t1:
    # Mostrar resumen de macros del día
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Proteína", f"{st.session_state.macros['p']} g")
    with m2: st.metric("Carbohidratos", f"{st.session_state.
