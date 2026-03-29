import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Cargar API Key
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Revisa tus Secrets en Streamlit (GEMINI_API_KEY).")

# 2. Interfaz
st.set_page_config(page_title="IA Nutrición", page_icon="💪")
st.markdown("# 🥗 Asistente de Nutrición")

archivo = st.file_uploader("Sube tu comida...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 Analizar"):
        with st.spinner("Analizando..."):
            try:
                # Usamos el nombre limpio del modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(["Analiza calorías y macros de esta comida.", img])
                st.success("¡Listo!")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error: {e}")
