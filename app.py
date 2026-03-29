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

# 2. CSS Minimalista
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    .stButton>button { border-radius: 12px; padding: 10px; font-weight: 600; width: 100%; }
    .next-btn>div>button { background-color: #007AFF; color: white; border: none; }
    .back-btn>div>button { background-color: #ffffff; color: #86868b; border: 1px solid #e0e0e0; }
    .card { background: #fcfcfc; padding: 15px; border-radius: 15px; border: 1px solid #f0f0f0; text-align: center; margin-bottom: 10px; }
    .card-val { font-size: 20px; font-weight: 600; color: #1d1d1f; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; }
    .unit-text { color: #007AFF; font-size: 14px; font-weight: 600; text-align: center; margin-bottom: 15px; }
    h1 { font-weight: 600; color: #1d1d1f; text-align: center; }
    .step-label { text-align: center; color: #007AFF; font-size: 12px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.user = {'sexo': 'Masculino', 'altura': 170, 'peso': 70.0, 'obj': 'Ganar masa muscular'}

def ir_a(n): st.session_state.paso = n

# --- PANTALLAS ---

# PASO 1: GÉNERO (Sin edad)
if st.session_state.paso == 1:
    st.markdown("<p class='step-label'>PASO 1 DE 4</p><h1>Tu Sexo</h1>", unsafe_allow_html=True)
    st.session_state.user['sexo'] = st.radio("Selecciona:", ["Masculino", "Femenino"], horizontal=True)
    st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
    st.button("Continuar ➡️", on_click=ir_a, args=(2,))
    st.markdown("</div>", unsafe_allow_html=True)

# PASO 2: ESTATURA
elif st.session_state.paso == 2:
    st.markdown("<p class='step-label'>PASO 2 DE 4</p><h1>Estatura</h1>", unsafe_allow_html=True)
    alt = st.number_input("Altura:", 100, 250, st.session_state.user['altura'])
    st.markdown(f"<p class='unit-text'>{alt} cm equivale a {alt/100} metros</p>", unsafe_allow_html=True)
    st.session_state.user['altura'] = alt
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("⬅️ Atrás", on_click=ir_a, args=(1,))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2: 
        st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
        st.button("Siguiente ➡️", on_click=ir_a, args=(3,))
        st.markdown("</div>", unsafe_allow_html=True)

# PASO 3: PESO
elif st.session_state.paso == 3:
    st.markdown("<p class='step-label'>PASO 3 DE 4</p><h1>Peso Corporal</h1>", unsafe_allow_html=True)
    peso = st.number_input("Peso:", 30.0, 250.0, st.session_state.user['peso'])
    st.markdown(f"<p class='unit-text'>{peso} kg equivale a {round(peso*2.204, 1)} libras</p>", unsafe_allow_html=True)
    st.session_state.user['peso'] = peso
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("⬅️ Atrás", on_click=ir_a, args=(2,))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2: 
        st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
        st.button("Siguiente ➡️", on_click=ir_a, args=(4,))
        st.markdown("</div>", unsafe_allow_html=True)

# PASO 4: OBJETIVO
elif st.session_state.paso == 4:
    st.markdown("<p class='step-label'>PASO 4 DE 4</p><h1>Objetivo</h1>", unsafe_allow_html=True)
    st.session_state.user['obj'] = st.selectbox("Meta:", ["Ganar masa muscular", "Perder grasa", "Mantenimiento"])
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("⬅️ Atrás", on_click=ir_a, args=(3,))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2: 
        if st.button("Finalizar ✨"):
            u = st.session_state.user
            cal = int(((10 * u['peso']) + (6.25 * u['altura'])) * 1.5)
            if "Ganar" in u['obj']: cal += 450
            st.session_state.metas = {"cal": cal, "prot": int(u['peso']*2.1), "gras": int(u['peso']*0.8), "fib": 30, "agua": round(u['peso']*0.035, 1)}
            st.session_state.paso = 5
            st.rerun()

# DASHBOARD FINAL
elif st.session_state.paso == 5:
    st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    m = st.session_state.metas
    cols = st.columns(5)
    lbs = [("Calorías", m['cal'], "kcal"), ("Proteína", m['prot'], "g"), ("Grasas", m['gras'], "g"), ("Fibra", m['fib'], "g"), ("Agua", m['agua'], "L")]
    for i, col in enumerate(cols):
        with col: st.markdown(f"<div class='card'><div class='card-lab'>{lbs[i][0]}</div><div class='card-val'>{lbs[i][1]}<small style='font-size:10px;'>{lbs[i][2]}</small></div></div>", unsafe_allow_html=True)
    st.divider()
    f = st.file_uploader("Escanear plato", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    if f:
        img = Image.open(f)
        st.image(img, use_container_width=True)
        with st.spinner("Analizando..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(["Analiza: Plato|Cal|Prot|Carb|Gras|Fib. Solo texto separado por |", img]).text.split('|')
            st.markdown(f"<h3 style='text-align:center;'>{res[0]}</h3>", unsafe_allow_html=True)
            res_cols = st.columns(5)
            for j, r_col in enumerate(res_cols):
                with r_col: st.markdown(f"<div class='card'><div class='card-lab'>{lbs[j][0]}</div><div class='card-val'>{res[j+1]}</div></div>", unsafe_allow_html=True)
    if st.button("Reiniciar Perfil"): ir_a(1); st.rerun()
