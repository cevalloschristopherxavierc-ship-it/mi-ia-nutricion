import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta API Key en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. CSS Estilo Fitia Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    .stButton>button { border-radius: 14px; padding: 10px; font-weight: 600; width: 100%; }
    .next-btn>div>button { background-color: #007AFF; color: white; border: none; }
    .back-btn>div>button { background-color: #ffffff; color: #86868b; border: 1px solid #e0e0e0; }
    .card { background: #fcfcfc; padding: 15px; border-radius: 18px; border: 1px solid #f0f0f0; text-align: center; margin-bottom: 10px; }
    .card-val { font-size: 20px; font-weight: 700; color: #1d1d1f; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; font-weight: 600; }
    .unit-label { color: #007AFF; font-size: 14px; font-weight: 600; text-align: center; margin-bottom: 10px; display: block; }
    h1 { font-weight: 700; color: #1d1d1f; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.user = {'sexo': 'Masculino', 'alt': 170, 'peso': 70.0, 'obj': 'Ganar masa muscular'}

def ir_a(n): st.session_state.paso = n

# --- PANTALLAS ---

if st.session_state.paso == 1:
    st.markdown("<h1>Tu Perfil</h1>", unsafe_allow_html=True)
    st.session_state.user['sexo'] = st.radio("Sexo Biológico:", ["Masculino", "Femenino"], horizontal=True)
    st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
    st.button("Siguiente ➡️", on_click=ir_a, args=(2,))
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 2:
    st.markdown("<h1>Estatura</h1>", unsafe_allow_html=True)
    alt = st.number_input("Altura actual:", 100, 250, st.session_state.user['alt'])
    st.markdown(f"<span class='unit-label'>{alt} cm / {alt/100} m</span>", unsafe_allow_html=True)
    st.session_state.user['alt'] = alt
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", on_click=ir_a, args=(1,)); st.markdown("</div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='next-btn'>", unsafe_allow_html=True); st.button("Siguiente ➡️", on_click=ir_a, args=(3,)); st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 3:
    st.markdown("<h1>Peso Corporal</h1>", unsafe_allow_html=True)
    peso = st.number_input("Peso actual:", 30.0, 250.0, st.session_state.user['peso'])
    st.markdown(f"<span class='unit-label'>{peso} kg / {round(peso*2.204, 1)} lbs</span>", unsafe_allow_html=True)
    st.session_state.user['peso'] = peso
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", on_click=ir_a, args=(2,)); st.markdown("</div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='next-btn'>", unsafe_allow_html=True); st.button("Siguiente ➡️", on_click=ir_a, args=(4,)); st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 4:
    st.markdown("<h1>Objetivo</h1>", unsafe_allow_html=True)
    st.session_state.user['obj'] = st.selectbox("Meta:", ["Ganar masa muscular", "Perder grasa", "Mantenimiento"])
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", on_click=ir_a, args=(3,)); st.markdown("</div>", unsafe_allow_html=True)
    with c2: 
        if st.button("Finalizar ✨"):
            u = st.session_state.user
            cal = int(((10 * u['peso']) + (6.25 * u['alt'])) * 1.5)
            if "Ganar" in u['obj']: cal += 450
            st.session_state.metas = {"cal": cal, "prot": int(u['peso']*2.1), "gras": int(u['peso']*0.8), "car": int(u['peso']*4), "agua": round(u['peso']*0.035, 1)}
            st.session_state.paso = 5
            st.rerun()

elif st.session_state.paso == 5:
    st.markdown("<h1>Resumen Diario</h1>", unsafe_allow_html=True)
    m = st.session_state.metas
    cols = st.columns(5)
    lbs = [("Calorías", m['cal'], "kcal"), ("Proteína", m['prot'], "g"), ("Grasas", m['gras'], "g"), ("Carbos", m['car'], "g"), ("Agua", m['agua'], "L")]
    for i, col in enumerate(cols):
        with col: st.markdown(f"<div class='card'><div class='card-lab'>{lbs[i][0]}</div><div class='card-val'>{lbs[i][1]}</div><div style='font-size:10px;'>{lbs[i][2]}</div></div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📸 Tomar Foto de Comida")
    f = st.file_uploader("Sube tu plato aquí...", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    if f:
        img = Image.open(f)
        st.image(img, use_container_width=True)
        with st.spinner("Analizando plato..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(["Responde en ESPAÑOL solo: Plato|Kcal|Prot|Carb|Gras. Sin más texto.", img]).text.split('|')
            if len(res) >= 5:
                st.success(f"Detección: {res[0]}")
                r_cols = st.columns(4)
                r_labels = [("Calorías", res[1], "kcal"), ("Proteína", res[2], "g"), ("Carbos", res[3], "g"), ("Grasas", res[4], "g")]
                for j, r_col in enumerate(r_cols):
                    with r_col: st.markdown(f"<div class='card' style='border-top:3px solid #007AFF'><div class='card-lab'>{r_labels[j][0]}</div><div class='card-val'>{r_labels[j][1]}</div></div>", unsafe_allow_html=True)
    
    if st.button("🔄 Reiniciar Perfil"): ir_a(1); st.rerun()
