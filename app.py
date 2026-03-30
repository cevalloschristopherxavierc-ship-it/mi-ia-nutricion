import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")

st.markdown("# 🥗 FitIA: Escáner 63kg")
st.info("Intentando conexión por vía de alta compatibilidad...")

f = st.file_uploader("📸 Sube la foto de tu comida", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 Analizar Plato"):
        with st.spinner("🤖 Jarvis usando modelo de respaldo..."):
            try:
                # CAMBIO RADICAL: Usamos el modelo 'gemini-pro-vision' que es el más compatible
                # Usamos la versión v1beta que es la que mejor maneja este modelo legacy
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={API_KEY}"
                
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
                
                r = requests.post(url, json=payload)
                data = r.json()
                
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
                    # SI EL MODELO PRO TAMBIÉN DA 404, INTENTAMOS EL ÚLTIMO MODELO DISPONIBLE
                    st.error("Google no encuentra el modelo Pro. Intentando última ruta...")
                    url_final = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
                    r = requests.post(url_final, json=payload)
                    st.json(r.json())
                    
            except Exception as e:
                st.error(f"Error de red: {e}")

if st.button("🔄 Reiniciar App"):
    st.rerun()
