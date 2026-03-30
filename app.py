import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ Configura la API Key en los Secrets de Streamlit.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilo CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; color: white; }
    .card { background: #1c1c1e; padding: 15px; border-radius: 15px; border: 1px solid #2c2c2e; text-align: center; margin-bottom: 8px; }
    .card-val { font-size: 20px; font-weight: 700; color: #ffffff; }
    .card-lab { font-size: 10px; color: #86868b; text-transform: uppercase; font-weight: 600; }
    .stButton>button { border-radius: 12px; background-color: #007AFF; color: white; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.u = {'alt': 170, 'peso': 63.0}

# (Código simplificado para ir directo al grano)
if st.session_state.paso < 5:
    st.markdown("# FitIA Pro")
    if st.button("Ir al Resumen Diario"):
        st.session_state.paso = 5
        st.rerun()

elif st.session_state.paso == 5:
    st.markdown("# Resumen Diario")
    
    # Tarjetas de ejemplo (puedes volver a poner tus cálculos aquí)
    cols = st.columns(4)
    for col, lab, val in zip(cols, ["Calorías", "Proteína", "Carbos", "Grasas"], [2300, 140, 280, 60]):
        with col: st.markdown(f"<div class='card'><div class='card-lab'>{lab}</div><div class='card-val'>{val}</div></div>", unsafe_allow_html=True)

    st.divider()
    f = st.file_uploader("📸 Escanear comida", type=["jpg", "jpeg", "png"])
    
    if f:
        img_bytes = f.read()
        st.image(img_bytes, use_container_width=True)
        
        if st.button("🔍 Analizar ahora"):
            with st.spinner("🤖 Conectando directamente con Google..."):
                try:
                    # CONEXIÓN MANUAL POR HTTP (Sin usar genai.GenerativeModel)
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    
                    headers = {'Content-Type': 'application/json'}
                    
                    # Convertir imagen a Base64
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')
                    
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "Responde SOLO: Nombre|Kcal|Prot|Carb|Gras"},
                                {"inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": base64_image
                                }}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, headers=headers, json=payload)
                    data = response.json()
                    
                    # Extraer texto de la respuesta
                    res_text = data['candidates'][0]['content']['parts'][0]['text']
                    res = res_text.strip().split('|')
                    
                    if len(res) >= 5:
                        st.success(f"Detección: {res[0]}")
                        r_cols = st.columns(4)
                        for j, r_col in enumerate(r_cols):
                            with r_col: st.markdown(f"<div class='card' style='border-top:3px solid #007AFF'><div class='card-lab'>{lab}</div><div class='card-val'>{res[j+1]}</div></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error de red: {e}")
                    st.write("Detalle técnico:", data if 'data' in locals() else "No hay respuesta")

    if st.button("🔄 Reiniciar"):
        st.session_state.paso = 1
        st.rerun()
