import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel Xavier", page_icon="📊", layout="wide")

# Estilo visual para clonar tu captura (Modo Oscuro con acentos en rojo/azul)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #888; }
    .metric-value { font-size: 24px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CABECERA: MÉTRICAS (Igual a tu foto) ---
st.title("📊 Panel Xavier")

col_kcal, col_prot, col_burn = st.columns(3)

with col_kcal:
    st.markdown('<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">52 / 2750</p></div>', unsafe_allow_html=True)
with col_prot:
    st.markdown('<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">0.3 / 139g</p></div>', unsafe_allow_html=True)
with col_burn:
    st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 3. NAVEGACIÓN (Pestañas como en tu foto) ---
tabs = st.tabs(["🍽️ REGISTRO", "🔍 ANÁLISIS", "📔 DIARIO", "🛠️ CREADOR"])

# --- 4. FUNCIÓN DE IA (MOTOR GEMINI 3.1) ---
def analizar_con_jarvis(image_file, api_key):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    model_name = "gemini-3.1-flash-lite-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": "Analiza esta comida. Dame calorías y macros (P/C/G). Sé breve y técnico para Xavier."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- 5. CONTENIDO DE PESTAÑAS ---

with tabs[0]: # REGISTRO
    col_ia, col_manual = st.columns(2)
    
    with col_ia:
        st.subheader("📷 Foto IA")
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            archivo = st.file_uploader("Sube plato", type=["jpg", "jpeg", "png"])
            if archivo:
                img = Image.open(archivo)
                st.image(img, use_container_width=True)
                if st.button("🔍 ANALIZAR"):
                    with st.spinner("Procesando..."):
                        res = analizar_con_
