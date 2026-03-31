import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾")

# --- 2. FUNCIÓN DE CONEXIÓN DIRECTA (SIN LIBRERÍAS) ---
def analizar_con_jarvis(image_file, api_key):
    # Convertir imagen a base64
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # URL oficial de Google (Versión estable v1)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": "Eres Jarvis. Analiza esta comida para Xavier. Dame calorías y macros (Proteína, Carb, Grasa) para hipertrofia de pierna y glúteo. Sé breve."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# --- 3. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.2")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ Falta API KEY en Secrets.")
    st.stop()

archivo = st.file_uploader("Sube tu plato...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("EJECUTAR ANÁLISIS"):
        with st.spinner("🤖 Jarvis analizando vía Direct-Link..."):
            try:
                res = analizar_con_jarvis(img, api_key)
                
                # Extraer el texto de la respuesta de Google
                if 'candidates' in res:
                    texto = res['candidates'][0]['content']['parts'][0]['text']
                    st.success("Análisis de Jarvis:")
                    st.markdown(texto)
                else:
                    st.error(f"Error de Google: {res}")
            except Exception as e:
                st.error(f"Error de sistema: {e}")

# Registro de Gym
st.markdown("---")
peso = st.number_input("Peso hoy (lb):", 0)
if st.button("GUARDAR"):
    st.info(f"Registro: {peso}lb guardado.")
