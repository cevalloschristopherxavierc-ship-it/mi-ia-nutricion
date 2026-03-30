import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configuración de API (El motor que ya funcionó)
API_KEY = st.secrets.get("GEMINI_API_KEY")
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

st.set_page_config(page_title="Jarvis Nutrición Pro", layout="centered", page_icon="💪")

# --- LÓGICA DE ESTADO (MEMORIA TEMPORAL) ---
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'total_prot' not in st.session_state:
    st.session_state.total_prot = 0.0

# Meta calculada para tus 63kg (2g de proteína por kilo)
META_PROT = 126.0 

# --- INTERFAZ VISUAL ---
st.title("💪 Jarvis: Modo Hipertrofia")
st.markdown(f"**Perfil:** 170cm | 63kg | 📍 Portoviejo")

# Sección de Progreso Diario
col_prog, col_stats = st.columns([2, 1])
with col_prog:
    st.write(f"### Proteína: {st.session_state.total_prot:.1f}g / {META_PROT}g")
    progreso = min(st.session_state.total_prot / META_PROT, 1.0)
    st.progress(progreso)
with col_stats:
    st.metric("Meta Diaria", f"{META_PROT}g")

st.divider()

# --- ESCÁNER DE COMIDA ---
st.subheader("📸 Escáner de Comida")
f = st.file_uploader("Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True, caption="Imagen cargada")
    
    if st.button("🔍 ANALIZAR Y GUARDAR"):
        with st.spinner("🤖 Jarvis calculando nutrientes..."):
            try:
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la comida. Responde estrictamente en este formato: Nombre|Kcal|Prot|Carb|Gras. No agregues texto extra."},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                        ]
                    }]
                }
                
                r = requests.post(MODEL_URL, json=payload)
                data = r.json()
                
                if 'candidates' in data:
                    res = data['candidates'][0]['content']['parts'][0]['text']
                    stats = res.split('|')
                    
                    if len(stats) >= 5:
                        nombre_plato = stats[0].strip()
                        kcal_val = stats[1].strip()
                        # Limpiamos el valor de proteína para sumarlo
                        p_texto = stats
