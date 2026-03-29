import streamlit as st
import google.generativeai as genai
from PIL import Image

# Esta línea busca la clave que guardaste en Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# Configuración de la página
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición y Fitness")

archivo_subido = st.file_uploader("Selecciona una foto...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None:
    imagen = Image.open(archivo_subido)
    st.image(imagen, use_container_width=True)
    
    if st.button("🔍 Analizar Nutrientes"):
        with st.spinner("Analizando..."):
            model = genai.GenerativeModel("gemini-1.5-flash")
            # El texto y la imagen bien organizados
            contenido = [
                "Analiza las calorías y macros de esta comida. Dime si sirve para ganar músculo.",
                imagen
            ]
            try:
                respuesta = model.generate_content(contenido)
                st.success("¡Análisis listo!")
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Error: {e}")
