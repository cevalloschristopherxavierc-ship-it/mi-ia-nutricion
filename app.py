import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la API
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("❌ Falta la clave en Secrets.")
    st.stop()

# 2. Interfaz
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición")

archivo = st.file_uploader("Sube tu comida...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 Analizar"):
        with st.spinner("Buscando modelo compatible..."):
            try:
                # Paso 1: Intentar con el modelo más moderno (Nombre estándar)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(["Analiza los macros de esta comida.", img])
                st.success("¡Conexión exitosa!")
                st.write(res.text)
                
            except Exception as e:
                # Paso 2: Si falla, buscamos qué modelos TIENE tu cuenta realmente
                st.warning("Reintentando con configuración alternativa...")
                try:
                    # Listamos los modelos que soportan generación de contenido
                    modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    
                    # Filtramos uno que sirva para imágenes (Flash o Pro)
                    modelo_final = next((m for m in modelos_disponibles if "flash" in m or "pro" in m), modelos_disponibles[0])
                    
                    model_alt = genai.GenerativeModel(modelo_final)
                    res = model_alt.generate_content(["Analiza los macros de esta comida.", img])
                    st.success(f"¡Conectado usando {modelo_final}!")
                    st.write(res.text)
                except Exception as e2:
                    st.error(f"Error crítico: {e2}")
                    st.info("Asegúrate de que tu API KEY no tenga restricciones de región en Google Cloud.")
