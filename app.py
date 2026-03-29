import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la clave API en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="⚪", layout="centered")

# 2. CSS Minimalista Profesional
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    
    .stButton>button {
        border-radius: 12px; padding: 10px; font-weight: 600; width: 100%; transition: 0.3s;
    }
    .next-btn>div>button { background-color: #007AFF; color: white; border: none; }
    .back-btn>div>button { background-color: #ffffff; color: #86868b; border: 1px solid #e0e0e0; }
    
    .card {
        background: #fcfcfc; padding: 15px; border-radius: 15px;
        border: 1px solid #f0f0f0; text-align: center; margin-bottom: 10px;
    }
    .card-val { font-size: 22px; font-weight: 600; color: #1d1d1f; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; letter-spacing: 1px; }
    
    .unit-text { color: #007AFF; font-size: 14px; font-weight: 600; margin-top: 2px; text-align: center; }
    h1 { font-weight: 600; color: #1d1d1f; text-align: center; letter-spacing: -1px; }
    .step-indicator { text-align: center; color: #007AFF; font-weight: 600; font-size: 12px; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.user = {'sexo': 'Masculino', 'altura': 170, 'peso': 70.0, 'obj': 'Ganar masa muscular'}

def ir_a(n):
    st.session_state.paso = n

# --- PANTALLAS ---

# PASO 1: GÉNERO
if st.session_state.paso == 1:
    st.markdown("<p class='step-indicator'>Paso 1 de 4</p><h1>Tu Sexo</h1>", unsafe_allow_html=True)
    st.session_state.user['sexo'] = st.radio("Selecciona:", ["Masculino", "Femenino"], horizontal=True)
    
    st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
    st.button("Continuar ➡️", on_click=ir_a, args=(2,))
    st.markdown("</div>", unsafe_allow_html=True)

# PASO 2: ESTATURA
elif st.session_state.paso == 2:
    st.markdown("<p class='step-indicator'>Paso 2 de 4</p><h1>Estatura</h1>", unsafe_allow_html=True)
    alt = st.number_input("Altura actual:", 100, 250, st.session_state.user['altura'])
    st.markdown(f"<p class='unit-text'>{alt} cm equivale a {alt/100} metros</p>", unsafe_allow_html=True)
    st.session_state.user['altura'] = alt
    
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", on_click=ir_a
