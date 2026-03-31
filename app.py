import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(page_title="Jarvis Core - Debug", page_icon="🦾")

def test_models(api_key):
    # Esta función le pregunta a Google: "¿Qué modelos me dejas usar?"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)
    return response.json()

def analizar_comida(image_file, api_key, model_name):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": "Analiza esta comida para hipertrofia. Dame macros y calorías."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    return requests.post(url, json=payload).json()

st.title("🦾 JARVIS CORE: DEBUG MODE")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # BOTÓN DE DIAGNÓSTICO
    if st.button("🔍 PASO 1: VERIFICAR MODELOS DISPONIBLES"):
        res = test_models(api_key)
        if 'models' in res:
            st.success("¡Llave conectada! Modelos que puedes usar:")
            # Listamos los modelos para ver si 'gemini-1.5-flash' aparece
            modelos = [m['name'] for m in res['models']]
            st.write(modelos)
            if 'models/gemini-1.5-flash' in modelos:
                st.info("✅ El modelo Flash ESTÁ disponible. El error era la ruta.")
            else:
                st.warning("❌ El modelo Flash NO está en tu lista. Intenta con 'gemini-pro-vision'.")
        else:
            st.error(f"Error de llave: {res}")

    st.markdown("---")
    
    # PASO 2: ANÁLISIS
    archivo = st.file_uploader("Sube tu plato...", type=["jpg", "jpeg", "png"])
    if archivo:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        
        if st.button("🚀 PASO 2: EJECUTAR ANÁLISIS"):
            # Intentamos con el nombre técnico exacto
            res_ia = analizar_comida(img, api_key, "gemini-1.5-flash")
            if 'candidates' in res_ia:
                st.markdown(res_ia['candidates'][0]['content']['parts'][0]['text'])
            else:
                st.error(f"Google dice: {res_ia.get('error', {}).get('message', 'Error desconocido')}")

else:
    st.error("No hay API Key en Secrets.")
