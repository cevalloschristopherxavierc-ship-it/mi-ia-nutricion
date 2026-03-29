import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Tu clave ya integrada:
API_KEY = "AIzaSyDDCESvGkob8chj4y2mU6Y1nmD1j-trA6g"
genai.configure(api_key=API_KEY)

# Configuración de la página
st.set_page_config(page_title="Mi Nutricionista IA", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición y Fitness")
st.write("Sube una foto de tu plato para analizar tus macros y calorías.")

# Interfaz de usuario
archivo_subido = st.file_uploader("Selecciona una foto de tu comida...", type=["jpg", "jpeg", "png"])

if archivo_subido is not None:
    imagen = Image.open(archivo_subido)
    st.image(imagen, caption='Tu plato actual', use_container_width=True)
    
    boton_analizar = st.button("🔍 Analizar Nutrientes")

    instrucciones = """
    Eres un experto en nutrición deportiva. Analiza la imagen y:
    1. Enumera los alimentos que ves.
    2. Calcula las calorías totales aproximadas.
    3. Dame los gramos de Proteínas, Carbohidratos y Grasas.
    4. Dime si esta comida ayuda a ganar masa muscular (hipertrofia).
    5. Dame un consejo rápido para mejorar el plato.
    Responde de forma breve y motivadora.
    """

    if boton_analizar:
        with st.spinner('La IA está examinando tu comida...'):
            try:
                modelo = genai.GenerativeModel('gemini-1.5-flash')
                respuesta = modelo.generate_content([instrucciones, imagen])
                st.success("¡Análisis listo!")
                st.markdown("### 📊 Resultado del Análisis:")
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Hubo un error: {e}")