import streamlit as st  # <-- ESTO DEBE IR PRIMERO
import google.generativeai as genai
from PIL import Image
import os

# 1. Configuración de API Segura
# Primero verificamos si Streamlit está cargado correctamente
try:
    if "GEMINI_API_KEY" in st.secrets:
        # Forzamos a la librería a usar la versión estable
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ Falta la clave 'GEMINI_API_KEY' en los Secrets de Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"Error al cargar secretos: {e}")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilo CSS Minimalista
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
    st.markdown(f"<span class='unit-tag'>{val} cm / {val/100:.2f} m</span>", unsafe_allow_html=True)
    st.session_state.u['alt'] = val
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", key="b1", on_click=ir, args=(1,)); st.markdown("</div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='next-btn'>", unsafe_allow_html=True); st.button("Siguiente ➡️", key="n2", on_click=ir, args=(3,)); st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 3:
    st.markdown("<h1>Peso</h1>", unsafe_allow_html=True)
    val = st.number_input("Peso (kg):", 30.0, 250.0, st.session_state.u['peso'])
    st.markdown(f"<span class='unit-tag'>{val} kg / {round(val*2.204, 1)} lbs</span>", unsafe_allow_html=True)
    st.session_state.u['peso'] = val
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", key="b2", on_click=ir, args=(2,)); st.markdown("</div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='next-btn'>", unsafe_allow_html=True); st.button("Siguiente ➡️", key="n3", on_click=ir, args=(4,)); st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.paso == 4:
    st.markdown("<h1>Objetivo</h1>", unsafe_allow_html=True)
    st.session_state.u['obj'] = st.selectbox("Meta:", ["Ganar masa muscular", "Perder grasa", "Mantenimiento"])
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='back-btn'>", unsafe_allow_html=True); st.button("⬅️ Atrás", key="b3", on_click=ir, args=(3,)); st.markdown("</div>", unsafe_allow_html=True)
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
    lbs = [("Calorías", m['cal'], "kcal"), ("Proteína", m['pro'], "g"), ("Grasas", m['gra'], "g"), ("Carbos", m['car'], "g"), ("Agua", m['h2o'], "L")]
    for i, col in enumerate(cols):
        with col: st.markdown(f"<div class='card'><div class='card-lab'>{lbs[i][0]}</div><div class='card-val'>{lbs[i][1]}</div><div style='font-size:10px;'>{lbs[i][2]}</div></div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📸 Escáner de Comida")
    f = st.file_uploader("Sube tu plato...", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if f:
        img = Image.open(f)
        st.image(img, use_container_width=True)
        with st.spinner("🤖 Analizando..."):
            try:
                # Usamos el nombre del modelo compatible
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Analiza esta comida. Responde SOLO: Nombre|Kcal|Prot|Carb|Gras. Sin nada más."
                response = model.generate_content([prompt, img])
                
                res = response.text.strip().split('|')
                if len(res) >= 5:
                    st.success(f"Detección: {res[0]}")
                    r_cols = st.columns(4)
                    r_lbs = [("Calorías", res[1], "kcal"), ("Proteína", res[2], "g"), ("Carbos", res[3], "g"), ("Grasas", res[4], "g")]
                    for j, r_col in enumerate(r_cols):
                        with r_col: st.markdown(f"<div class='card' style='border-top:3px solid #007AFF'><div class='card-lab'>{r_lbs[j][0]}</div><div class='card-val'>{r_lbs[j][1]}</div></div>", unsafe_allow_html=True)
                else:
                    st.warning("Formato no reconocido. Intenta con otra foto clara.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    
    if st.button("🔄 Reiniciar Perfil", key="reset"):
        st.session_state.paso = 1
        st.rerun()
