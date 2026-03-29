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

# 2. CSS Minimalista con Enfoque en Unidades
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    
    /* Botones de Navegación */
    .stButton>button {
        border-radius: 12px; padding: 10px; font-weight: 600; width: 100%; transition: 0.3s;
    }
    .next-btn>div>button { background-color: #007AFF; color: white; border: none; }
    .back-btn>div>button { background-color: #ffffff; color: #86868b; border: 1px solid #e0e0e0; }
    
    /* Tarjetas de Dashboard */
    .card {
        background: #fcfcfc; padding: 15px; border-radius: 15px;
        border: 1px solid #f0f0f0; text-align: center; margin-bottom: 10px;
    }
    .card-val { font-size: 22px; font-weight: 600; color: #1d1d1f; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Etiquetas de Unidades (kg, cm, etc) */
    .unit-hint { 
        color: #007AFF; font-size: 13px; font-weight: 600; 
        margin-top: -15px; margin-bottom: 15px; display: block;
    }
    
    h1 { font-weight: 600; color: #1d1d1f; text-align: center; letter-spacing: -1px; }
    .step-text { text-align: center; color: #007AFF; font-weight: 600; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.user = {'sexo': 'Masculino', 'edad': 25, 'altura': 170, 'peso': 70.0, 'obj': 'Ganar masa muscular'}

def set_step(s): st.session_state.step = s

# --- PANTALLAS ---

# PASO 1: GÉNERO Y EDAD
if st.session_state.step == 1:
    st.markdown("<p class='step-text'>PASO 1 DE 4</p><h1>Perfil Básico</h1>", unsafe_allow_html=True)
    st.session_state.user['sexo'] = st.selectbox("Selecciona tu Sexo", ["Masculino", "Femenino"])
    st.session_state.user['edad'] = st.number_input("Introduce tu Edad", 10, 100, st.session_state.user['edad'])
    st.markdown("<span class='unit-hint'>años</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
    st.button("Siguiente", on_click=set_step, args=(2,))
    st.markdown("</div>", unsafe_allow_html=True)
