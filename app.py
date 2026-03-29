import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición y Fitness")

# 1. Cargar API Key desde Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("Configura la GEMINI_API_KEY en los Secrets de Streamlit.")

archivo_subido = st.file_uploader("Sube la foto de tu comida...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None:
    imagen = Image.open(archivo_subido)
    st.image(imagen, use_container_width=True)
    
    if st.button("🔍 Analizar Nutrientes"):
        with st.spinner("Analizando con Gemini 1.5..."):
            try:
                # Usamos el nombre directo del modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Respuesta de la IA
                respuesta = model.generate_content([
                    "Analiza esta comida para un atleta en Portoviejo. Dime calorías, proteínas, carbohidratos y grasas. ¿Ayuda al desarrollo de pierna y glúteo?", 
                    imagen
                ])
                
                st.success("¡Análisis completado!")
                st.markdown(respuesta.text)
                
            except Exception as e:
                st.error(f"Error técnico: {e}")
                st.info("Si el error persiste, asegúrate de haber actualizado el archivo requirements.txt")
