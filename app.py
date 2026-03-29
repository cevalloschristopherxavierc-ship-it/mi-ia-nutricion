import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta configuración de API.")
    st.stop()

# Configuración de página minimalista
st.set_page_config(page_title="FitIA", page_icon="⚪", layout="centered")

# 2. CSS Minimalista (Blanco Puro y Azul Eléctrico)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    
    /* Contenedor principal */
    .main { background-color: #ffffff; }
    
    /* Botones Minimalistas */
    .stButton>button {
        border-radius: 50px; padding: 10px 24px; background-color: #007AFF;
        color: white; border: none; font-weight: 500; transition: 0.3s; width: 100%;
    }
    .stButton>button:hover { background-color: #0056b3; box-shadow: 0 4px 15px rgba(0,122,255,0.3); }

    /* Tarjetas de Datos */
    .card {
        background: #fcfcfc; padding: 20px; border-radius: 20px;
        border: 1px solid #f0f0f0; text-align: center; margin-bottom: 10px;
    }
    .card-val { font-size: 28px; font-weight: 600; color: #1d1d1f; margin-bottom: 0px; }
    .card-lab { font-size: 12px; color: #86868b; text-transform: uppercase; letter-spacing: 1px; }
    .unit { font-size: 14px; color: #007AFF; font-weight: 600; }

    /* Inputs Estilizados */
    .stNumberInput, .stSelectbox { border-radius: 15px; }
    
    /* Títulos */
    h1 { font-weight: 600; color: #1d1d1f; letter-spacing: -1px; text-align: center; }
    p { text-align: center; color: #86868b; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.user = {}

def next_step(): st.session_state.step += 1
def reset(): st.session_state.step = 1

# --- PANTALLAS ---

if st.session_state.step == 1:
    st.markdown("<h1>Identidad</h1><p>Define tu perfil básico</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user['sexo'] = st.selectbox("Sexo", ["Masculino", "Femenino"])
    with col2:
        st.session_state.user['edad'] = st.number_input("Edad", 10, 90, 25)
    st.button("Continuar", on_click=next_step)

elif st.session_state.step == 2:
    st.markdown("<h1>Dimensiones</h1><p>Tus medidas actuales</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        # Estatura con conversión visual
        altura = st.number_input("Estatura", 100, 230, 170)
        st.markdown(f"<span class='unit'>{altura} cm / {round(altura/100, 2)} m</span>", unsafe_allow_html=True)
        st.session_state.user['altura'] = altura
    with c2:
        # Peso con conversión visual
        peso = st.number_input("
