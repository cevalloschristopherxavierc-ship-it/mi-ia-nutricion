import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ Configura la clave en Secrets de Streamlit.")
    st.stop()

# 2. Interfaz
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición")

archivo = st.file_uploader("Sube tu comida...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 Analizar"):
        with st.spinner("Cambiando estrategia de conexión..."):
            try:
                # CAMBIO CLAVE: Usamos la versión 1.0 que es "blindada" contra errores 404
                model = genai.GenerativeModel('gemini-1.0-pro-vision-latest')
                
                # En esta versión, el orden de los factores importa
                res = model.generate_content([
                    "Analiza las calorías y macros de esta comida para hipertrofia.", 
                    img
                ])
                
                st.success("¡Por fin conectamos!")
                st.write(res.text)
            except Exception as e:
                # Si falla, intentamos la última ruta posible
                try:
                    model_fallback = genai.GenerativeModel('models/gemini-1.5-flash')
                    res = model_fallback.generate_content(["Analiza la imagen", img])
                    st.write(res.text)
                except:
                    st.error(f"Error persistente: {e}")
