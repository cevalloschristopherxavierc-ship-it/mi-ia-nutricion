import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTILO JARVIS) ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE APIS (SECRETS) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. EL CEREBRO DE LA IA (PROMPT DE NUTRICIÓN) ---
SISTEMA_EXPERTO = """
Eres un Nutriólogo experto en Hipertrofia y Rendimiento Deportivo. 
Analiza la imagen de comida que se te proporciona y entrega lo siguiente:
1. Identificación precisa de cada alimento.
2. Un APROXIMADO detallado de:
   - Calorías totales.
   - Proteínas (g) - Crucial para la recuperación muscular.
   - Carbohidratos (g).
   - Grasas (g).
3. EVALUACIÓN DE HIPERTROFIA: ¿Es este plato adecuado para un entrenamiento intenso de pierna/glúteo?
4. AJUSTE RECOMENDADO: ¿Qué debería añadir o quitar para optimizar el crecimiento muscular?
Responde con un tono técnico, eficiente y motivador, al estilo de una IA avanzada (Jarvis).
"""

# --- 4. INTERFAZ DE USUARIO ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")
st.markdown("---")

# Dividimos la pantalla en dos columnas
col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("🍎 Escaneo de Biomasa (Nutrición)")
    archivo = st.file_uploader("Sube la foto de tu comida, Xavier...", type=["jpg", "png", "jpeg"])

    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Imagen captada por el sensor", use_column_width=True)
        
        if st.button("EJECUTAR ANÁLISIS DE MACROS"):
            with st.spinner("🤖 Jarvis está procesando los datos nutricionales..."):
                try:
                    resultado = model.generate_content([SISTEMA_EXPERTO, img])
                    st.success("Análisis completado:")
                    st.markdown(resultado.text)
                except Exception as e:
                    st.error(f"Error en el análisis: {e}")

with col_der:
    st.subheader("📺 Control de Entorno")
    if st.button("ENCENDER CHRIS-TV"):
        if "IFTTT_KEY" in st.secrets:
            url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{st.secrets['IFTTT_KEY']}"
            try:
                res = requests.post(url)
                if res.status_code == 200:
                    st.success("🤖 Señal enviada a la nube. Encendiendo...")
                else:
                    st.error("Error al conectar con IFTTT.")
            except:
                st.error("No se pudo enviar la señal.")
        else:
            st.warning("⚠️ Configura 'IFTTT_KEY' para usar esta función.")

    st.markdown("---")
    st.subheader("🏋️ Registro de Cargas")
    ejercicio = st.selectbox("Ejercicio del día:", ["Smith Machine Lunges", "Hip Thrust", "RDL", "Sentadilla Búlgara"])
    peso = st.number_input("Peso cargado (unidades):", min_value=0)
    reps = st.number_input("Repeticiones:", min_value=0)
    
    if st.button("GUARDAR SET"):
        st.info(f"Registro: {ejercicio} | {peso} kg/lb | {reps} reps. ¡Buen trabajo, Xavier!")

# --- 5. BARRA LATERAL (ESTADO DEL SISTEMA) ---
st.sidebar.header("📈 Estado del Sistema")
st.sidebar.write("**Usuario:** Xavier Cevallos")
st.sidebar.write("**Ubicación:** Portoviejo, Manabí")
st.sidebar.write("**Meta:** Hipertrofia de Tren Inferior")
st.sidebar.progress(100)
st.sidebar.write("✅ Servidor Estable")
