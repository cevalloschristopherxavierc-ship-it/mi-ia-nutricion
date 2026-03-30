import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Portoviejo", layout="centered")
st.markdown("# 🥗 Jarvis Nutrición 2026")
st.info("Perfil: 170cm | 63kg | Hipertrofia")

f = st.file_uploader("📸 Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 Analizar Macros"):
        with st.spinner("🤖 Jarvis analizando con tecnología Gemini 2.0..."):
            try:
                # Usamos el nombre exacto de tu lista exitosa
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la comida de la imagen. Responde solo en este formato: Nombre|Kcal|Prot|Carb|Gras"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
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
                        c2.metric("Proteína", f"{stats[2]}g")
                        c3.metric("Carbos", f"{stats[3]}g")
                        c4.metric("Grasas", f"{stats[4]}g")
                elif 'error' in data and data['error']['code'] == 429:
                    st.warning("⏳ Google está activando tu cuota gratuita. Espera 20 segundos y vuelve a presionar el botón.")
                else:
                    st.error("Error de configuración de modelos.")
                    st.json(data)
            except Exception as e:
                st.error(f"Error de conexión: {e}")

if st.button("🔄 Reiniciar"):
    st.rerun()
