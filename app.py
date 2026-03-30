import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")
st.markdown("# 🥗 Jarvis Nutrición")

f = st.file_uploader("📸 Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 Analizar ahora"):
        with st.spinner("🤖 Jarvis probando ruta de respaldo..."):
            try:
                # CAMBIO CLAVE: Usamos 'gemini-pro-vision' en lugar de 'flash'
                # Usamos v1beta que es la versión que mejor soporta este modelo
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={API_KEY}"
                
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la comida. Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                        ]
                    }]
                }
                
                r = requests.post(url, json=payload)
                data = r.json()
                
                if 'candidates' in data:
                    res = data['candidates'][0]['content']['parts'][0]['text']
                    st.success(f"🍴 Resultado: {res}")
                else:
                    # Si falla, intentamos la ruta Pro 1.5
                    url_pro = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
                    r2 = requests.post(url_pro, json=payload)
                    st.json(r2.json())
            except Exception as e:
                st.error(f"Error: {e}")
