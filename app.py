import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core - System V2.1", page_icon="🦾", layout="wide")

# Estilo visual personalizado
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #00d4ff; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIÓN MAESTRA DE ANÁLISIS (GEMINI 3.1) ---
def analizar_con_jarvis(image_file, api_key, objetivo, calorias_meta):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    model_name = "gemini-3.1-flash-lite-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = f"""
    Actúa como Jarvis, experto en nutrición para Xavier Cevallos.
    Objetivo actual: {objetivo}. Meta diaria: {calorias_meta} kcal.
    Enfoque: Hipertrofia de pierna y glúteo.
    Analiza la imagen y entrega:
    1. Identificación de alimentos.
    2. Macros (Prot, Carb, Fat) y Calorías.
    3. Porcentaje que este plato representa de su meta diaria.
    4. Recomendación técnica para optimizar el crecimiento muscular hoy.
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# --- 3. BARRA LATERAL: PERFIL Y METAS ---
st.sidebar.header("👤 Perfil: Xavier Cevallos")
objetivo = st.sidebar.radio("Objetivo del Ciclo:", ["Ganancia de Masa (Bulk)", "Definición (Cut)", "Mantenimiento"])
cal_meta = st.sidebar.number_input("Meta Calorías Diarias:", value=2800, step=50)

st.sidebar.markdown("---")
st.sidebar.subheader("💧 Hidratación")
if 'vasos' not in st.session_state: st.session_state.vasos = 0
col_h1, col_h2 = st.sidebar.columns(2)
if col_h1.button("➕ Agua"): st.session_state.vasos += 1
if col_h2.button("➖"): st.session_state.vasos = max(0, st.session_state.vasos - 1)
st.sidebar.metric("Vasos de agua", f"{st.session_state.vasos} / 12")

# --- 4. INTERFAZ PRINCIPAL ---
st.title("🦾 JARVIS CORE: INTEGRATED SYSTEM")

tabs = st.tabs(["🍎 Nutrición", "👣 Actividad", "📊 Progreso"])

with tabs[0]:
    st.subheader("Escaneo de Biomasa Nutricional")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        archivo =
