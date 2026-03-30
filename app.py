import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")

# --- INTERFAZ ---
st.markdown("# 🥗 FitIA: Escáner Final")
st.info("Perfil: 170cm | 63kg | Ganar Masa Muscular")

f = st.file_uploader("📸 Sube la foto de tu comida", type=["jpg", "jpeg", "png"])

if f:
    # Leer imagen y prepararla
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 Analizar Plato"):
        with st.spinner("🤖 Jarvis conectando por túnel directo..."):
            try:
                # URL DIRECTA (Sin pasar por librerías internas)
                # Intentamos la versión v1beta que es la más flexible para imágenes
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
                # Convertir imagen a formato que Google entiende directamente
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la imagen. Responde estrictamente: Nombre|Kcal|Prot|Carb|Gras"},
                            {"inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_img
                            }}
                        ]
                    }]
                }
                
                # Petición directa al servidor de Google
                response = requests.post(url, json=payload)
                data = response.json()
                
                # Si esto falla, intentamos la versión v1 (estable) automáticamente
                if 'error' in data and data['error']['code'] == 404:
                    url_v1 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    response = requests.post(url_v1, json=payload)
                    data = response.json()

                if 'candidates' in data:
                    res = data['candidates'][0]['content']['parts'][0]['text']
                    stats = res.split('|')
                    if len(stats) >= 5:
                        st.success(f"🍴 {stats[0]}")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Kcal", stats[1])
                        c2.metric("Prot", f"{stats[2]}g")
                        c3.metric("Carb", f"{stats[3]}g")
                        c4.metric("Gras", f"{stats[4]}g")
                else:
                    st.error("❌ Error de Google:")
                    st.json(data)
                    
            except Exception as e:
                st.error(f"Error de red: {e}")

if st.button("🔄 Reiniciar App"):
    st.rerun()
