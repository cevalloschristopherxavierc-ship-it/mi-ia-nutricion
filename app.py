import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Configuración de API con Forzado de Endpoint
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Configura la API Key en los Secrets de Streamlit.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilo CSS
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
    h1 { font-weight: 700; color: #1d1d1f; text-align: center; letter-spacing: -1px; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.u = {'sexo': 'Masculino', 'alt': 170, 'peso': 70.0, 'obj': 'Ganar masa muscular'}

def ir(n):
    st.session_state.paso = n

# --- PANTALLAS ---
if st.session_state.paso == 1:
    st.markdown("<h1>Tu Perfil</h1>", unsafe_allow_html=True)
    st.session_state.u['sexo'] = st.radio("Sexo:", ["Masculino", "Femenino"], horizontal=True)
    st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
    st.button("Siguiente ➡️", key="n1", on_click=ir, args=(2,))
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 2:
    st.markdown("<h1>Estatura</h1>", unsafe_allow_html=True)
    val = st.number_input("Altura (cm):", 100, 250, st.session_state.u['alt'])
    st.session_state.u['alt'] = val
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("⬅️ Atrás", key="b1", on_click=ir, args=(1,))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2: 
        st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
        st.button("Siguiente ➡️", key="n2", on_click=ir, args=(3,))
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 3:
    st.markdown("<h1>Peso</h1>", unsafe_allow_html=True)
    val = st.number_input("Peso (kg):", 30.0, 250.0, st.session_state.u['peso'])
    st.session_state.u['peso'] = val
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("⬅️ Atrás", key="b2", on_click=ir, args=(2,))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2: 
        st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
        st.button("Siguiente ➡️", key="n3", on_click=ir, args=(4,))
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 4:
    st.markdown("<h1>Objetivo</h1>", unsafe_allow_html=True)
    st.session_state.u['obj'] = st.selectbox("Meta:", ["Ganar masa muscular", "Perder grasa", "Mantenimiento"])
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("⬅️ Atrás", key="b3", on_click=ir, args=(3,))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.button("Finalizar ✨", key="fin"):
            u = st.session_state.u
            calBase = int(((10 * u['peso']) + (6.25 * u['alt'])) * 1.5)
            if "Ganar" in u['obj']: calBase += 450
            st.session_state.m = {"cal": calBase, "pro": int(u['peso']*2.1), "gra": int(u['peso']*0.8), "car": int(u['peso']*4), "h2o": round(u['peso']*0.035, 1)}
            st.session_state.paso = 5
            st.rerun()

elif st.session_state.paso == 5:
    st.markdown("<h1>Resumen Diario</h1>", unsafe_allow_html=True)
    m = st.session_state.m
    cols = st.columns(5)
