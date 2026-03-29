import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave API
API_KEY="AIzaSyDDCESvGkob8chj4y2mU6Y1nmD1j-trA6g"
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
            # El orden correcto: Texto primero, luego la imagen
            contenido = [
                "Analiza las calorías y macros de esta comida. Dime si sirve para ganar músculo.",
                imagen
            ]
            try:
                respuesta = model.generate_content(contenido)
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Error: {e}")
