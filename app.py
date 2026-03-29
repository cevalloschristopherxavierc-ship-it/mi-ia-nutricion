import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la API
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("❌ Configura GEMINI_API_KEY en los Secrets.")
    st.stop()

# 2. Interfaz
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición")

archivo = st.file_uploader("Sube la foto de tu comida...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 Analizar Nutrientes"):
        with st.spinner("Analizando con Gemini 1.5 Flash..."):
            try:
                # Nombre exacto y moderno del modelo
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                res = model.generate_content(["Analiza calorías y macros de esta imagen:", img])
                st.success("¡Listo!")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
