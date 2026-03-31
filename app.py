import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core v2.2", page_icon="🦾", layout="wide")

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #00d4ff; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00d4ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROTOCOLO DE INICIO (PREGUNTAS) ---
st.sidebar.title("🔋 ESTADO DEL SISTEMA")
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])
    st.write(f"Estado: {humor} - {energia}")

# --- 3. METAS Y HORARIOS ---
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Objetivos")
objetivo = st.sidebar.selectbox("Meta de Peso:", ["Subir (Volumen Limpio)", "Bajar (Definición)", "Mantener"])
cal_meta = st.sidebar.number_input("Meta Calorías Diarias:", value=2800)

st.sidebar.subheader("📅 Cronograma Sugerido")
st.sidebar.info("""
- **07:00:** Desayuno Proteico
- **10:00:** Snack (Fruta/Frutos Secos)
- **13:00:** Almuerzo (Bulk Focus)
- **16:00:** Pre-Entreno (Carbs Rápidos)
- **19:00:** Cena (Post-Entreno Pierna)
""")

# --- 4. HIDRATACIÓN ---
st.sidebar.markdown("---")
st.sidebar.subheader("💧 Hidratación")
if 'agua' not in st.session_state: st.session_state.agua = 0
c1, c2 = st.sidebar.columns(2)
if c1.button("➕ Agua"): st.session_state.agua += 1
if c2.button("➖"): st.session_state.agua = max(0, st.session_state.agua - 1)
st.sidebar.metric("Progreso", f"{st.session_state.agua} / 12 vasos")

# --- 5. FUNCIÓN DE IA (GEMINI 3.1) ---
def analizar_con_jarvis(image_file, api_key, objetivo, cal_meta):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    model_name = "gemini-3.1-flash-lite-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = f"""
    Actúa como Jarvis. Usuario: Xavier Cevallos. 
    Objetivo: {objetivo}. Calorías meta: {cal_meta}.
    Analiza la imagen y entrega: 
    1. Identificación de biomasa (comida). 
    2. Calorías y Macros (P/C/G). 
    3. Evaluación para hipertrofia de pierna y glúteo. 
    4. ¿Cómo encaja este plato en su horario actual ({datetime.now().strftime('%H:%M')})?
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- 6. INTERFAZ PRINCIPAL ---
st.
