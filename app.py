import streamlit as st
import requests
import base64

API_KEY = st.secrets.get("GEMINI_API_KEY")
st.set_page_config(page_title="FitIA Pro", layout="centered")

st.markdown("# 🥗 Jarvis Nutrición")

f = st.file_uploader("📸 Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 Analizar Plato"):
        with st.spinner("🤖 Jarvis buscando modelo compatible..."):
            try:
                # Intentamos con el modelo más estándar y actual a la fecha
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
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
                    st.error("🚨 Google sigue sin reconocer el modelo.")
                    # ESTO NOS DIRÁ QUÉ MODELOS SÍ TIENES PERMITIDOS
                    st.write("Intentando listar modelos disponibles para tu cuenta...")
                    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
                    list_r = requests.get(list_url)
                    st.json(list_r.json())
            except Exception as e:
                st.error(f"Error: {e}")

if st.button("🔄 Reiniciar"):
    st.rerun()
