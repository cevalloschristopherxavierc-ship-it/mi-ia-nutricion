import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. FORZAR VERSIÓN ESTABLE (FIX 404) ---
# Esta línea le dice a la librería de Google que ignore la v1beta
os.environ["GOOGLE_API_VERSION"] = "v1"

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾")

# --- 3. CONFIGURACIÓN DE IA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    try:
        # Usamos el nombre del modelo sin prefijos para máxima compatibilidad
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de núcleo: {e}")
else:
    st.error("⚠️ Falta API KEY en Secrets.")

# --- 4. LÓGICA DE NUTRICIÓN ---
SISTEMA_EXPERTO = "Eres experto en nutrición para hipertrofia. Analiza la imagen y da calorías y macros."

st.title("🦾 JARVIS CORE: SCANNER")

archivo = st.file_uploader("Sube tu plato...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR"):
        with st.spinner("🤖 Jarvis analizando..."):
            try:
                # LLAMADA LIMPIA
                response = model.generate_content([SISTEMA_EXPERTO, img])
                st.success("Análisis:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error persistente: {e}")
                st.info("Xavier, si esto sigue, intenta crear una API KEY nueva en AI Studio. Las llaves viejas a veces se quedan 'atrapadas' en la versión beta.")

# --- 5. LOG GYM ---
st.markdown("---")
peso = st.number_input("Peso (lb):", min_value=0)
if st.button("GUARDAR"):
    st.success(f"Registrado: {peso}lb")
