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
        with st.spinner("🤖 Jarvis procesando macros..."):
            try:
                # Usamos 1.5-flash que es el que tiene la cuota gratuita más estable
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
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
                    # Separar los datos para que se vea profesional
                    stats = res.split('|')
                    if len(stats) >= 5:
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Kcal", stats[1])
                        c2.metric("Proteína", f"{stats[2]}g")
                        c3.metric("Carbos", f"{stats[3]}g")
                        c4.metric("Grasas", f"{stats[4]}g")
                else:
                    st.warning("⚠️ Google está saturado. Espera 30 segundos y presiona el botón otra vez.")
                    st.json(data)
            except Exception as e:
                st.error(f"Error: {e}")
