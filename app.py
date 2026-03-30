import streamlit as st
import requests
import base64

# Configuración
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")
st.markdown("# 🥗 Jarvis Nutrición")

f = st.file_uploader("📸 Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 Analizar ahora"):
        with st.spinner("🤖 Jarvis conectando..."):
            try:
                # Usamos la ruta estable v1
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
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
                    st.error("Revisa si habilitaste la API en el link azul.")
                    st.json(data)
            except Exception as e:
                st.error(f"Error: {e}")
