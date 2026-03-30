import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Falta API Key en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilo CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; color: white; }
    .stButton>button { border-radius: 12px; padding: 10px; font-weight: 600; width: 100%; background-color: #007AFF; color: white; border: none; }
    .card { background: #1c1c1e; padding: 15px; border-radius: 15px; border: 1px solid #2c2c2e; text-align: center; margin-bottom: 8px; }
    .card-val { font-size: 20px; font-weight: 700; color: #ffffff; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; font-weight: 600; }
    h1 { font-weight: 700; color: #ffffff; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    # Datos iniciales basados en tu perfil
    st.session_state.u = {'sexo': 'Masculino', 'alt': 170, 'peso': 63.0, 'obj': 'Ganar masa muscular'}

def ir(n):
    st.session_state.paso = n

# --- PANTALLAS ---

if st.session_state.paso == 1:
    st.markdown("<h1>Tu Perfil</h1>", unsafe_allow_html=True)
    st.session_state.u['sexo'] = st.radio("Sexo:", ["Masculino", "Femenino"], horizontal=True)
    st.button("Siguiente ➡️", on_click=ir, args=(2,))

elif st.session_state.paso == 2:
    st.markdown("<h1>Estatura</h1>", unsafe_allow_html=True)
    st.session_state.u['alt'] = st.number_input("Altura (cm):", 100, 250, st.session_state.u['alt'])
    st.button("Siguiente ➡️", on_click=ir, args=(3,))

elif st.session_state.paso == 3:
    st.markdown("<h1>Peso</h1>", unsafe_allow_html=True)
    st.session_state.u['peso'] = st.number_input("Peso (kg):", 30.0, 250.0, st.session_state.u['peso'])
    st.button("Siguiente ➡️", on_click=ir, args=(4,))

elif st.session_state.paso == 4:
    st.markdown("<h1>Objetivo</h1>", unsafe_allow_html=True)
    st.session_state.u['obj'] = st.selectbox("Meta:", ["Ganar masa muscular", "Perder grasa", "Mantenimiento"])
    
    if st.button("Finalizar ✨"):
        u = st.session_state.u
        # Cálculo de macros (ajustado a tus 63kg actuales)
        calBase = int(((10 * u['peso']) + (6.25 * u['alt'])) * 1.5)
        if "Ganar" in u['obj']: calBase += 500
        
        st.session_state.m = {
            "cal": calBase, 
            "pro": int(u['peso'] * 2.2), 
            "gra": int(u['peso'] * 0.9), 
            "car": int(u['peso'] * 4.5)
        }
        st.session_state.paso = 5
        st.rerun()

elif st.session_state.paso == 5:
    st.markdown("<h1>Resumen Diario</h1>", unsafe_allow_html=True)
    
    # Mostrar tarjetas de Macros
    m = st.session_state.m
    cols = st.columns(4)
    items = [("Calorías", m['cal'], "kcal"), ("Proteína", m['pro'], "g"), ("Carbos", m['car'], "g"), ("Grasas", m['gra'], "g")]
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class='card'>
                    <div class='card-lab'>{items[i][0]}</div>
                    <div class='card-val'>{items[i][1]}</div>
                    <div style='font-size:10px; color:#86868b;'>{items[i][2]}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # ESCÁNER
    st.markdown("### 📸 Analizar Plato")
    f = st.file_uploader("Sube una foto de tu comida", type=["jpg", "jpeg", "png"])
    
    if f:
        img = Image.open(f)
        st.image(img, use_container_width=True)
        if st.button("🔍 Escanear ahora"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = "Analiza la imagen. Responde SOLO: Nombre|Kcal|Prot|Carb|Gras"
                    response = model.generate_content([prompt, img])
                    res = response.text.strip().split('|')
                    
                    if len(res) >= 5:
                        st.success(f"Detección: {res[0]}")
                        r_cols = st.columns(4)
                        for j, r_col in enumerate(r_cols):
                            with r_col:
                                st.markdown(f"<div class='card' style='border-top:3px solid #007AFF'><div class='card-lab'>{items[j][0]}</div><div class='card-val'>{res[j+1]}</div></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.button("🔄 Reiniciar Perfil"):
        st.session_state.paso = 1
        st.rerun()
