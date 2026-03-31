import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core v2.2", page_icon="🦾", layout="wide")

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #00d4ff; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00d4ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROTOCOLO DE INICIO (PREGUNTAS) ---
st.sidebar.title("🔋 ESTADO DEL SISTEMA")
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia_input = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor_input = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])
    st.write(f"Estado: {humor_input} - {energia_input}")

# --- 3. METAS Y HORARIOS ---
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Objetivos")
objetivo = st.sidebar.selectbox("Meta de Peso:", ["Subir (Volumen)", "Bajar (Definición)", "Mantener"])
cal_meta = st.sidebar.number_input("Meta Calorías Diarias:", value=2800)

st.sidebar.subheader("📅 Cronograma Sugerido")
st.sidebar.info("- **07:00:** Desayuno\n- **10:00:** Snack\n- **13:00:** Almuerzo\n- **16:00:** Pre-Entreno\n- **19:00:** Cena")

# --- 4. HIDRATACIÓN ---
st.sidebar.markdown("---")
st.sidebar.subheader("💧 Hidratación")
if 'agua' not in st.session_state: st.session_state.agua = 0
c1, c2 = st.sidebar.columns(2)
if c1.button("➕ Agua"): st.session_state.agua += 1
if c2.button("➖"): st.session_state.agua = max(0, st.session_state.agua - 1)
st.sidebar.metric("Progreso", f"{st.session_state.agua} / 12 vasos")

# --- 5. FUNCIÓN DE IA (GEMINI 3.1) ---
def analizar_con_jarvis(image_file, api_key, objetivo, cal_meta):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    model_name = "gemini-3.1-flash-lite-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = f"Jarvis, analiza esta comida para Xavier Cevallos. Objetivo: {objetivo}. Calorías meta: {cal_meta}. Enfócate en hipertrofia de pierna y glúteo. Da macros y evalúa según la hora local: {datetime.now().strftime('%H:%M')}."

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- 6. INTERFAZ PRINCIPAL ---
st.title("🦾 JARVIS CORE: INTEGRATED SYSTEM V2.2")

t1, t2, t3 = st.tabs(["🍎 NUTRICIÓN", "👣 MOVIMIENTO", "📊 LOGS"])

with t1:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        archivo = st.file_uploader("Escanear biomasa...", type=["jpg", "jpeg", "png"])
        if archivo:
            img = Image.open(archivo)
            st.image(img, use_container_width=True)
            if st.button("ANALIZAR PLATO"):
                with st.spinner("🤖 Analizando..."):
                    res = analizar_con_jarvis(img, api_key, objetivo, cal_meta)
                    if 'candidates' in res:
                        st.markdown(res['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error("Error en conexión.")
    else:
        st.error("Falta API KEY.")

with t2:
    st.subheader("Control de Pasos")
    pasos = st.number_input("Pasos hoy:", min_value=0, value=8000)
    st.progress(min(pasos/10000, 1.0), text=f"Progreso: {pasos}/10,000")
    entreno = st.selectbox("Sesión:", ["Piernas", "Torso", "Fútbol", "Descanso"])
    if st.button("GUARDAR ACTIVIDAD"):
        st.success(f"Día de {entreno} registrado.")

with t3:
    st.subheader("Historial de Fuerza")
    ejer = st.text_input("Ejercicio:", placeholder="Ej. Hip Thrust")
    peso = st.number_input("Peso:", 0)
    if st.button("GUARDAR RÉCORD"):
        st.info(f"Registrado: {ejer} - {peso}")

# --- 7. ESTADO ---
st.sidebar.markdown("---")
st.sidebar.write(f"Sistema: **ONLINE ✅** | {datetime.now().strftime('%H:%M')}")
