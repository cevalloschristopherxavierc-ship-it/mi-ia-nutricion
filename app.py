import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Configura la API Key en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA - Registro", page_icon="⚖️", layout="centered")

# 2. Estilo Azul Premium y Blanco
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e3a8a; }
    .stButton>button { 
        background-color: #2563eb; color: white; border-radius: 12px; 
        width: 100%; height: 50px; font-weight: bold; border: none; font-size: 18px;
    }
    .macro-card { 
        background-color: #f8fafc; padding: 15px; border-radius: 15px; 
        text-align: center; border: 1px solid #e2e8f0; border-top: 5px solid #2563eb;
    }
    .val { font-size: 22px; font-weight: bold; color: #1e3a8a; }
    .lab { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
    .unit-label { font-size: 14px; font-weight: bold; color: #3b82f6; }
    h1, h2 { color: #1e3a8a; text-align: center; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN PASO A PASO ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.datos = {}

# PANTALLAS DE CONFIGURACIÓN
if st.session_state.paso == 1:
    st.title("🛡️ Paso 1: Perfil Básico")
    st.session_state.datos['genero'] = st.radio("Selecciona tu Sexo:", ["Masculino", "Femenino"], horizontal=True)
    st.session_state.datos['edad'] = st.number_input("Introduce tu Edad:", 10, 100, 25)
    if st.button("Siguiente ➡️"): st.session_state.paso = 2; st.rerun()

elif st.session_state.paso == 2:
    st.title("📏 Paso 2: Medidas Físicas")
    
    # Estatura con unidad al lado
    st.markdown("<p class='unit-label'>Estatura actual:</p>", unsafe_allow_html=True)
    st.session_state.datos['altura'] = st.number_input("Centímetros (cm)", 100, 250, 170, help="Ejemplo: 170 cm")
    
    st.divider()
    
    # Peso con unidad al lado
    st.markdown("<p class='unit-label'>Peso corporal:</p>", unsafe_allow_html=True)
    st.session_state.datos['peso'] = st.number_input("Kilogramos (kg)", 30.0, 200.0, 70.0, help="Ejemplo: 70.5 kg")
    
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("⬅️ Atrás"): st.session_state.paso = 1; st.rerun()
    with col2:
        if st.button("Siguiente ➡️"): st.session_state.paso = 3; st.rerun()

elif st.session_state.paso == 3:
    st.title("🎯 Paso 3: Objetivo Final")
    st.session_state.datos['objetivo'] = st.selectbox("¿Cuál es tu meta?", ["Ganar masa muscular", "Perder grasa corporal", "Mantener salud"])
    
    if st.button("CALCULAR REQUERIMIENTOS 🚀"):
        d = st
