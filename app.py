import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN INICIAL (LA QUE TE FUNCIONA) ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONEXIÓN CON LAS LLAVES ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

# AQUÍ ESTÁ EL ARREGLO DEL ERROR 404:
# Agregamos 'models/' antes del nombre para que el servidor lo encuentre siempre.
model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- 3. EL PROMPT DE NUTRICIÓN (TU LÓGICA DE SIEMPRE) ---
SISTEMA_EXPERTO = """
Actúa como un experto en nutrición y entrenamiento de hipertrofia.
Analiza la imagen de comida y entrega:
1. Identificación de los alimentos.
2. Aproximado de Calorías, Proteínas, Carbohidratos y Grasas.
3. Evaluación: ¿Es buena para ganar músculo en las piernas y glúteos?
4. Consejo de Jarvis: ¿Qué le falta a este plato?
Responde de forma técnica y directa.
"""

# --- 4. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("🍎 Análisis de Comida")
    archivo = st.file_uploader("Sube tu foto aquí...", type=["jpg", "png", "jpeg"])

    if archivo:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        
        if st.button("ANALIZAR MACROS"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    # Ejecutamos el análisis con tu lógica original
                    resultado = model.generate_content([SISTEMA_EXPERTO, img])
                    st.markdown("### 📊 Resultado:")
                    st.write(resultado.text)
                except Exception as e:
                    st.error(f"Error en el análisis: {e}")

with col_der:
    st.subheader("📺 Control")
    if st.button("ENCENDER TELE"):
        if "IFTTT_KEY" in st.secrets:
            url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{st.secrets['IFTTT_KEY']}"
            requests.post(url)
            st.success("Señal enviada.")
        else:
            st.warning("Falta IFTTT_KEY")

    st.markdown("---")
    st.subheader("🏋️ Gym Log")
    ejer = st.text_input("Ejercicio:")
    peso = st.number_input("Peso:", min_value=0)
    if st.button("Guardar"):
        st.success(f"Registrado: {ejer} con {peso}")

# Barra lateral simple
st.sidebar.write("Usuario: Xavier Cevallos")
st.sidebar.write("Estado: Conectado")
