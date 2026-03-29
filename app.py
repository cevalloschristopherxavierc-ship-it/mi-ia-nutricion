import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la API forzando la versión estable
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    # Forzamos el transporte a 'rest' para evitar problemas de red
    genai.configure(api_key=API_KEY, transport='rest')
except Exception as e:
    st.error("Error con la API Key en Secrets.")

# 2. Configuración visual
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición y Fitness")

archivo_subido = st.file_uploader("Selecciona una foto...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None:
    imagen = Image.open(archivo_subido)
    st.image(imagen, use_container_width=True)
    
    if st.button("🔍 Analizar Nutrientes"):
        with st.spinner("Analizando con IA..."):
            try:
                # Especificamos el modelo estándar
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Enviamos la petición
                respuesta = model.generate_content([
                    "Analiza esta comida. Dime: 1. Calorías aprox. 2. Macros (P/C/G). 3. ¿Es buena para ganar músculo?", 
                    imagen
                ])
                
                st.success("¡Análisis completado!")
                st.write(respuesta.text)
            except Exception as e:
                # Si esto falla, probamos con el nombre alternativo del modelo
                try:
                    model_alt = genai.GenerativeModel("models/gemini-1.5-flash")
                    respuesta = model_alt.generate_content(["Analiza la imagen", imagen])
                    st.write(respuesta.text)
                except:
                    st.error(f"Error persistente: {e}")
