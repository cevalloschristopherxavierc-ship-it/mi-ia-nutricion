import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Configuración de API e Interfaz
if "GEMINI_API_KEY" in st.secrets:
    # Forzamos a que no use rutas experimentales v1beta
    os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Configura la API Key en los Secrets de Streamlit.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilo Visual (Estilo Fitia)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    .stButton>button { border-radius: 12px; padding: 10px; font-weight: 600; width: 100%; }
    .next-btn>div>button { background-color: #007AFF; color: white; border: none; }
    .back-btn>div>button { background-color: #ffffff; color: #86868b; border: 1px solid #e0e0e0; }
    .card { background: #fcfcfc; padding: 15px; border-radius: 15px; border: 1px solid #f0f0f0; text-align: center; margin-bottom: 8px; }
    .card-val { font-size: 20px; font-weight: 700; color: #1d1d1f; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; font-weight: 600; }
    .unit-tag { color: #007AFF; font-size: 13px; font-weight: 600; display: block; text-align: center; margin-bottom: 10px; }
    h1 { font-weight: 700; color: #1d1d1f; text-align: center; letter-spacing: -1px; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.u = {'sexo': 'Masculino', 'alt': 170, 'peso': 70.0, 'obj': 'Ganar masa muscular'}

def ir(n):
    st.session_state.paso = n

# --- FLUJO DE PANTALLAS ---
if st.session_state.paso == 1:
    st.markdown("<h1>Tu Perfil</h1>", unsafe_allow_html=True)
    st.session_state.u['sexo'] = st.radio("Sexo:", ["Masculino", "Femenino"], horizontal=True)
    st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
    st.button("Siguiente ➡️", key="n1", on_click=ir, args=(2,))
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 2:
    st.markdown("<h1>Estatura</h1>", unsafe_allow_html=True)
    val = st.number_input("Altura (cm):", 100, 250, st.session_state.u['alt'])
    st.markdown(f"<span class='unit-tag'>{val} cm / {val/100:.2f} m</span>", unsafe_allow_html=True)
    st.session_state.u['alt'] = val
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", key="b1", on_click=ir, args=(1,)); st.markdown("</div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='next-btn'>", unsafe_allow_html=True); st.
