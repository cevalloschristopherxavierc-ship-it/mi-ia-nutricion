import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾")

# --- CONEXIÓN CON GOOGLE (FIX 404) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usamos la configuración más básica para evitar conflictos de versión
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Falta GOOGLE_API_KEY en Secrets.")

# --- INTERFAZ ---
st.title("🦾 JARVIS CORE")

archivo = st.file_uploader("Sube tu comida...", type=["jpg", "jpeg", "png"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR"):
        try:
            # Prompt ultra-directo
            response = model.generate_content(["Analiza macros y calorías de esta comida para hipertrofia.", img])
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# --- BOTÓN TELE ---
st.markdown("---")
if st.button("ENCENDER TELE"):
    if "IFTTT_KEY" in st.secrets:
        url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{st.secrets['IFTTT_KEY']}"
        requests.post(url)
        st.success("Señal enviada.")
