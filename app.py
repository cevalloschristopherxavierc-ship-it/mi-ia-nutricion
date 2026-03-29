import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración básica
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición y Fitness")

# Cargar API Key
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Revisa tus Secrets en Streamlit.")

archivo_subido = st.file_uploader("Sube tu comida...", type=["jpg", "png", "jpeg"])

if archivo_subido:
    imagen = Image.open(archivo_subido)
    st.image(imagen, use_container_width=True)
    
    if st.button("🔍 Analizar"):
        with st.spinner("Analizando..."):
            try:
                # Usamos el nombre corto del modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                respuesta = model.generate_content(["Analiza calorías y macros de esta imagen", imagen])
                st.success("¡Listo!")
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Error: {e}")
