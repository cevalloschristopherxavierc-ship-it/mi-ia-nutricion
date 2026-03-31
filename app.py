import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE LA IA (FIX TOTAL DEL 404) ---
if "GOOGLE_API_KEY" in st.secrets:
    # Configuramos la API
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # FORZAMOS EL MODELO ESTABLE (Sin el prefijo models/ para que no se confunda la v1beta)
    # Si este falla, el bloque try-except intentará la alternativa
    try:
        # Usamos el nombre del modelo tal cual, sin rutas extras
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al inicializar: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets.")

# --- 3. PROMPT DE NUTRICIÓN (TU LÓGICA DE SIEMPRE) ---
SISTEMA_EXPERTO = """
Actúa como Nutriólogo experto en Hipertrofia.
Analiza la imagen de comida y entrega:
1. Alimentos detectados.
2. Aprox de: Calorías, Proteínas (g), Carbohidratos (g) y Grasas (g).
3. ¿Es óptimo para piernas/glúteos?
4. ¿Qué falta para mejorar el plato?
Responde breve, técnico y motivador como Jarvis.
"""

# --- 4. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("🍎 Escaneo de Nutrientes")
    archivo = st.file_uploader("Sube tu foto, Xavier...", type=["jpg", "png", "jpeg"])

    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Imagen cargada", use_container_width=True)
        
        if st.button("ANALIZAR AHORA"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    # PROBAMOS EL MÉTODO ESTABLE
                    response = model.generate_content(
                        contents=[SISTEMA_EXPERTO, img]
                    )
                    st.success("Análisis completado:")
                    st.markdown(response.text)
                except Exception as e:
                    # SI FALLA EL PRIMERO, INTENTAMOS CON LA RUTA 'models/'
                    try:
                        model_alt = genai.GenerativeModel('models/gemini-1.5-flash')
                        response_alt = model_alt.generate_content([SISTEMA_EXPERTO, img])
                        st.markdown(response_alt.text)
                    except:
                        st.error(f"Error persistente: {e}")
                        st.warning("⚠️ Posible solución: Ve a Google AI Studio y crea una LLAVE NUEVA. A veces las llaves viejas se quedan en la versión beta.")

with col_der:
    st.subheader("📺 Control")
    if st.button("ENCENDER TELE"):
        key = st.secrets.get("IFTTT_KEY", "bQpyH6xT10n6e2YJsTXE_oK22s7GQTLuqEiMFNNrvDd")
        url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{key}"
        requests.post(url)
        st.success("Comando enviado.")

    st.markdown("---")
    st.subheader("🏋️ Log Gym")
    ejer = st.selectbox("Ejercicio:", ["Smith Lunges", "Hip Thrust", "RDL"])
    peso = st.number_input("Peso:", min_value=0)
    if st.button("GUARDAR"):
        st.info(f"Guardado: {ejer} a {peso}")
