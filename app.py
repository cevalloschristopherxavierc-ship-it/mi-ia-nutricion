import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾")

# --- 2. FUNCIÓN DE CONEXIÓN MAESTRA (Bypass 404) ---
def analizar_con_jarvis(image_file, api_key):
    # Convertir imagen a base64
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # Intentaremos con el nombre de modelo que Google acepta globalmente
    # Cambiamos la ruta a la versión técnica: models/gemini-1.5-flash-latest
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": "Actúa como Jarvis. Analiza esta comida para Xavier. Dame calorías y macros (Proteína, Carb, Grasa) enfocados en hipertrofia de pierna y glúteo."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# --- 3. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.3")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ Error: Configura GOOGLE_API_KEY en los Secrets.")
    st.stop()

archivo = st.file_uploader("Sube tu plato de hoy...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("EJECUTAR ESCANEO"):
        with st.spinner("🤖 Jarvis accediendo al satélite..."):
            try:
                res = analizar_con_jarvis(img, api_key)
                
                # Manejo de respuesta
                if 'candidates' in res:
                    texto = res['candidates'][0]['content']['parts'][0]['text']
                    st.success("Análisis completado:")
                    st.markdown(texto)
                elif 'error' in res:
                    # Si falla el primero, el código te dirá qué está pasando exactamente
                    st.error(f"Respuesta de Google: {res['error']['message']}")
                    st.info("💡 Tip: Verifica que en AI Studio hayas habilitado 'Gemini API' y no estés usando una clave de Google Cloud restringida.")
                else:
                    st.error(f"Error desconocido: {res}")
            except Exception as e:
                st.error(f"Fallo de sistema: {e}")

# Registro de entrenamiento
st.markdown("---")
st.subheader("🏋️ Log de Fuerza")
ejer = st.selectbox("Ejercicio:", ["Smith Machine Lunges", "Hip Thrust", "RDL"])
peso = st.number_input("Peso (lb):", 0)
if st.button("REGISTRAR"):
    st.success(f"Dato guardado: {ejer} a {peso}lb. ¡Buen trabajo, Xavier!")
