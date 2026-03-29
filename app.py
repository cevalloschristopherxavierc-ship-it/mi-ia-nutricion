import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Conexión segura con los Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("Error con la API Key en Secrets. Revisa la configuración.")

# 2. Configuración visual
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición y Fitness")

archivo_subido = st.file_uploader("Selecciona una foto...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None:
    imagen = Image.open(archivo_subido)
    st.image(imagen, use_container_width=True)
    
    if st.button("🔍 Analizar Nutrientes"):
        with st.spinner("Analizando con IA..."):
            # Usamos el nombre base que es el más compatible hoy
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            try:
                # Enviamos la imagen y el texto juntos
                respuesta = model.generate_content([
                    "Analiza esta comida. Dime: 1. Calorías aprox. 2. Macros (P/C/G). 3. ¿Es buena para hipertrofia?", 
                    imagen
                ])
                st.success("¡Análisis completado!")
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Hubo un problema al procesar la imagen: {e}")
