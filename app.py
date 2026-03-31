import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# Configuración ultra-básica
st.set_page_config(page_title="Jarvis Core", layout="wide")

# Conexión Segura
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Configura la GOOGLE_API_KEY en los Secrets de Streamlit.")

st.title("🦾 JARVIS CORE")

# Selector de archivos
archivo = st.file_uploader("Sube tu comida...", type=["jpg", "jpeg", "png"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR"):
        try:
            # Prompt directo para evitar errores de lectura
            response = model.generate_content(["Analiza los macros y calorías de esta comida para mis metas de gimnasio.", img])
            st.success("Análisis de Jarvis:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error de la IA: {e}")

# Botón de la Tele
st.markdown("---")
if st.button("ENCENDER TELE"):
    if "IFTTT_KEY" in st.secrets:
        url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{st.secrets['IFTTT_KEY']}"
        requests.post(url)
        st.info("Comando de encendido enviado.")
