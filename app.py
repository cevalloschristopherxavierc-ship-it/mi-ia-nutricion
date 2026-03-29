import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuración de API (Seguridad ante todo)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Falta la clave API en Streamlit Secrets. La IA no funcionará.")
    st.stop()

# Configuración de página minimalista
st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. CSS Minimalista Premium (Estilo Apple/Fitia)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; color: #1d1d1f; }
    
    /* Botones de Navegación */
    .stButton>button { border-radius: 14px; padding: 12px 20px; font-weight: 600; font-size: 16px; transition: 0.3s; width: 100%; }
    .next-btn>div>button { background-color: #007AFF; color: white; border: none; }
    .next-btn>div>button:hover { background-color: #005ecb; box-shadow: 0 4px 12px rgba(0,122,255,0.3); }
    .back-btn>div>button { background-color: #ffffff; color: #86868b; border: 1px solid #e0e0e0; }
    .back-btn>div>button:hover { background-color: #f5f5f7; border-color: #d2d2d7; }
    
    /* Tarjetas de Macros (Dashboard y Resultados) */
    .macro-container { display: flex; gap: 10px; justify-content: space-between; margin-bottom: 20px; }
    .card { flex: 1; background: #fcfcfc; padding: 15px; border-radius: 18px; border: 1px solid #f0f0f0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .card-val { font-size: 22px; font-weight: 700; color: #1d1d1f; line-height: 1; }
    .card-unit { font-size: 12px; color: #1d1d1f; font-weight: 500; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; font-weight: 600; }
    
    /* Sección de Escáner */
    .scan-header { text-align: center; margin-top: 30px; margin-bottom: 20px; }
    .scan-title { font-size: 24px; font-weight: 700; color: #1d1d1f; }
    .scan-subtitle { font-size: 16px; color: #86868b; }
    
    /* Estilos generales */
    h1 { font-weight: 700; color: #1d1d1f; text-align: center; letter-spacing: -1px; }
    .unit-text { color: #007AFF; font-size: 15px; font-weight: 600; text-align: center; margin-bottom: 15px; display: block; }
    .step-label { text-align: center; color: #007AFF; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN (Se mantiene estable) ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.user = {'sexo': 'Masculino', 'altura': 170, 'peso':
