import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Intentar cargar la clave con el nombre EXACTO de Secrets
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("❌ No encontré 'GEMINI_API_KEY' en los Secrets de Streamlit.")
    st.stop() # Esto detiene la app para que no dé el error 404 de antes

# 2. Interfaz sencilla
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición")

archivo = st.file_uploader("Sube tu comida...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 Analizar"):
        with st.spinner("Analizando con Gemini 1.5..."):
            try:
                # Usamos el modelo más estable
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(["Analiza las calorías y macros de esta comida.", img])
                st.success("¡Listo!")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
