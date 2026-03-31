import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (SOLUCIÓN RADICAL) ---
if "GOOGLE_API_KEY" in st.secrets:
    # Limpiamos cualquier configuración previa
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    try:
        # CAMBIO CLAVE: Usamos 'gemini-1.5-flash-latest'
        # Este nombre es el más compatible actualmente
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error(f"Error al despertar a Jarvis: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets.")

# --- 3. LÓGICA DE NUTRICIÓN ---
SISTEMA_EXPERTO = """
Actúa como Jarvis, experto en nutrición para hipertrofia de pierna y glúteo.
Analiza la imagen de comida de Xavier y entrega:
1. Alimentos. 2. Macros aprox (Cal, Prot, Carb, Fat).
3. Evaluación para ganar masa muscular.
4. ¿Qué falta para optimizar el plato?
Sé breve, técnico y motivador.
"""

# --- 4. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")

archivo = st.file_uploader("Sube tu plato, Xavier...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR MACROS"):
        with st.spinner("🤖 Jarvis analizando..."):
            try:
                # Intento de generación con el nuevo nombre de modelo
                response = model.generate_content([SISTEMA_EXPERTO, img])
                st.success("Análisis completado:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error persistente: {e}")
                st.info("💡 XAVIER: Si esto falla, el problema es tu API KEY. Ve a AI Studio, crea una NUEVA y asegúrate de elegir 'Gemini API' y no una de 'Google Cloud'.")

# --- 5. CONTROL ---
if st.button("ENCENDER CHRIS-TV"):
    key = st.secrets.get("IFTTT_KEY", "bQpyH6xT10n6e2YJsTXE_oK22s7GQTLuqEiMFNNrvDd")
    url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{key}"
    requests.post(url)
    st.success("Señal enviada a la tele.")
