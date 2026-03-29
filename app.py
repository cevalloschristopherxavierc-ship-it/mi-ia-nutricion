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

# 2. Diseño Minimalista (Blanco y Azul Premium)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    .stButton>button {
        border-radius: 50px; padding: 12px; background-color: #007AFF;
        color: white; border: none; font-weight: 600; width: 100%;
    }
    .card {
        background: #fcfcfc; padding: 15px; border-radius: 15px;
        border: 1px solid #f0f0f0; text-align: center; margin-bottom: 10px;
    }
    .card-val { font-size: 24px; font-weight: 600; color: #1d1d1f; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; letter-spacing: 1px; }
    .unit-tag { font-size: 13px; color: #007AFF; font-weight: 500; margin-top: 5px; display: block; }
    h1 { font-weight: 600; color: #1d1d1f; text-align: center; letter-spacing: -1px; }
    p { text-align: center; color: #86868b; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.user = {}

def next_step(): st.session_state.step += 1
def reset(): st.session_state.step = 1

# --- PANTALLAS PASO A PASO ---

if st.session_state.step == 1:
    st.markdown("<h1>Identidad</h1><p>Paso 1 de 3</p>", unsafe_allow_html=True)
    st.session_state.user['sexo'] = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"])
    st.session_state.user['edad'] = st.number_input("Edad", 10, 95, 25)
    st.button("Siguiente", on_click=next_step)

elif st.session_state.step == 2:
    st.markdown("<h1>Medidas</h1><p>Paso 2 de 3</p>", unsafe_allow_html=True)
    
    # Altura con conversión m/cm
    alt = st.number_input("Estatura", 100, 250, 170)
    st.markdown(f"<span class='unit-tag'>{alt} cm equivale a {alt/100} metros</span>", unsafe_allow_html=True)
    st.session_state.user['altura'] = alt
    
    st.divider()
    
    # Peso con conversión kg/lbs
    peso = st.number_input("Peso Corporal", 30.0, 250.0, 70.0)
    st.markdown(f"<span class='unit-tag'>{peso} kg equivale a {round(peso*2.204, 1)} libras</span>", unsafe_allow_html=True)
    st.session_state.user['peso'] = peso
    
    st.button("Siguiente", on_click=next_step)

elif st.session_state.step == 3:
    st.markdown("<h1>Meta</h1><p>Paso 3 de 3</p>", unsafe_allow_html=True)
    obj = st.selectbox("Tu objetivo", ["Ganar masa muscular", "Perder grasa", "Salud General"])
    
    if st.button("Finalizar y Calcular"):
        u = st.session_state.user
        # Cálculo
