import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    st.error("Falta API Key en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", layout="centered")

# --- INTERFAZ ---
st.markdown("# 🥗 FitIA: Escáner 63kg")
st.info("Objetivo: Ganar masa muscular")

f = st.file_uploader("📸 Sube la foto de tu comida", type=["jpg", "jpeg", "png"])

if f:
    img = Image.open(f)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 Analizar Plato"):
        with st.spinner("🤖 Jarvis probando conexión segura..."):
            # Intentamos primero con Flash, si falla, saltamos a Pro
            modelos = ["gemini-1.5-flash", "gemini-1.5-pro"]
            exito = False
            
            for m_name in modelos:
                try:
                    model = genai.GenerativeModel(m_name)
                    prompt = "Responde solo: Nombre|Kcal|Prot|Carb|Gras. Ejemplo: Pollo|500|40|50|10"
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.success(f"✅ ¡Conectado con {m_name}!")
                        st.write(f"Detección: {response.text}")
                        exito = True
                        break
                except Exception:
                    continue
            
            if not exito:
                st.error("❌ Google sigue bloqueando la conexión.")
                st.info("Asegúrate de haber creado la clave en un 'NUEVO PROYECTO' en AI Studio.")

if st.button("🔄 Reiniciar App"):
    st.rerun()
