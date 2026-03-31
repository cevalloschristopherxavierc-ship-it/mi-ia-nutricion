import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core v2.0", page_icon="🦾", layout="wide")

# --- 2. FUNCIÓN DE ANÁLISIS (ACTUALIZADA A GEMINI 3.1) ---
def analizar_con_jarvis(image_file, api_key):
    # Convertir imagen a base64
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # USAMOS EL MODELO 3.1 FLASH (El más moderno de tu lista)
    model_name = "gemini-3.1-flash-lite-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": "Actúa como Jarvis. Analiza esta comida para Xavier. Dame calorías y macros (Proteína, Carb, Grasa) enfocados en hipertrofia de pierna y glúteo. Sé técnico y motivador."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# --- 3. INTERFAZ ---
st.title("🦾 JARVIS CORE: GENERATION 3")
st.markdown("---")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ Configura la API KEY en Secrets.")
    st.stop()

archivo = st.file_uploader("Sube tu biomasa (comida)...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("EJECUTAR ANÁLISIS"):
        with st.spinner("🤖 Jarvis procesando con Gemini 3.1..."):
            try:
                res = analizar_con_jarvis(img, api_key)
                
                if 'candidates' in res:
                    texto = res['candidates'][0]['content']['parts'][0]['text']
                    st.success("Análisis de Jarvis:")
                    st.markdown(texto)
                else:
                    st.error(f"Error de Google: {res.get('error', {}).get('message', 'Error desconocido')}")
            except Exception as e:
                st.error(f"Fallo de sistema: {e}")

# --- 4. LOG DE ENTRENAMIENTO ---
st.markdown("---")
st.subheader("🏋️ Registro de Fuerza")
ejer = st.selectbox("Ejercicio:", ["Smith Machine Lunges", "Hip Thrust", "RDL", "Sentadilla Búlgara"])
peso = st.number_input("Peso (lb/kg):", 0)
if st.button("GUARDAR EN EL NÚCLEO"):
    st.success(f"Dato guardado: {ejer} con {peso}. ¡A por la hipertrofia!")
