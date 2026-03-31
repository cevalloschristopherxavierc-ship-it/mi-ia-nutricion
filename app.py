import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel Xavier - Jarvis Core", page_icon="🦾", layout="wide")

# Estilo visual para clonar tu captura (Oscuro con métricas resaltadas)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-label { font-size: 16px; color: #8b949e; margin-bottom: 5px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 5px;
        padding: 10px 20px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CABECERA: MÉTRICAS SUPERIORES (Igual a tu captura) ---
st.title("📊 Panel Xavier: Jarvis Core")

col_kcal, col_prot, col_burn = st.columns(3)
with col_kcal:
    st.markdown('<div class="metric-box"><p class="metric-label">🔥 Kcal Consumidas</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
with col_prot:
    st.markdown('<div class="metric-box"><p class="metric-label">🍗 Proteína (g)</p><p class="metric-value">0 / 160g</p></div>', unsafe_allow_html=True)
with col_burn:
    st.markdown('<div class="metric-box"><p class="metric-label">🏃 Pasos / Cardio</p><p class="metric-value">0 / 10k</p></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 3. NAVEGACIÓN POR PESTAÑAS ---
tabs = st.tabs(["🚀 REGISTRO", "🔋 ESTADO", "📅 DIARIO/HORARIOS", "🛠️ CONFIG"])

# --- 4. FUNCIÓN DE IA (GEMINI 3.1 FLASH) ---
def analizar_con_jarvis(image_file, api_key, objetivo):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    model_name = "gemini-3.1-flash-lite-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = f"Eres Jarvis. Analiza esta comida para Xavier. Objetivo: {objetivo}. Da macros (P/C/G) y evalúa según la hora: {datetime.now().strftime('%H:%M')}."

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

# --- 5. CONTENIDO DE LAS PESTAÑAS ---

with tabs[0]: # REGISTRO (FOTO IA + MANUAL)
    col_foto, col_manual = st.columns(2)
    with col_foto:
        st.subheader("📷 Escaneo Visual")
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            archivo = st.file_uploader("Sube tu plato", type=["jpg", "jpeg", "png"])
            if archivo:
                img = Image.open(archivo)
                st.image(img, use_container_width=True)
                if st.button("EJECUTAR ANÁLISIS"):
                    with st.spinner("🤖 Jarvis analizando biomasa..."):
                        res = analizar_con_jarvis(img, api_key, "Ganancia Muscular")
                        if 'candidates' in res:
                            st.success("Informe de Nutrientes:")
                            st.markdown(res['candidates'][0]['content']['parts'][0]['text'])
        else:
            st.error("⚠️ Falta API KEY en Secrets.")

    with col_manual:
        st.subheader("✍️ Registro Manual/Pasos")
        pasos_input = st.number_input("Pasos hoy:", value=0)
        comida_nom = st.text_input("Nombre del alimento")
        if st.button("➕ GUARDAR ACTIVIDAD"):
            st.toast("Datos sincronizados con el núcleo.")

with tabs[1]: # ESTADO (PREGUNTAS DE DESPERTAR)
    st.subheader("🔋 Reporte de Estado Inicial")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        energia = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    with col_e2:
        humor = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])
    st.info(f"Jarvis reporta: Usuario en estado {humor} con energía {energia}.")

with tabs[2]: # DIARIO Y HORARIOS
    st.subheader("📅 Cronograma y Diario")
    col_h, col_d = st.columns([1, 2])
    with col_h:
        st.info("""
        **Horarios Portoviejo:**
        - 07:00: Desayuno
        - 13:00: Almuerzo
        - 16:00: Pre-Entreno
        - 19:00: Cena
        """)
    with col_d:
        st.write(f"Registro del día: {datetime.now().strftime('%d/%m/%Y')}")
        st.write("✅ Hidratación iniciada.")
        st.write("⏳ Esperando escaneo de almuerzo...")

with tabs[3]: # CONFIGURACIÓN
    st.subheader("🛠️ Parámetros del Sistema")
    objetivo_sel = st.radio("Ciclo actual:", ["Volumen Limpio", "Definición (Cut)", "Mantenimiento"])
    st.write(f"Hora de sincronización: {datetime.now().strftime('%H:%M')}")

# --- 6. BARRA LATERAL: HIDRATACIÓN ---
st.sidebar.title("💧 HIDRATACIÓN")
if 'agua' not in st.session_state: st.session_state.agua = 0
c1, c2 = st.sidebar.columns(2)
if c1.button("➕ Agua"): st.session_state.agua += 1
if c2.button("➖"): st.session_state.agua = max(0, st.session_state.agua - 1)
st.sidebar.metric("Vasos", f"{st.session_state.agua} / 12")
st.sidebar.markdown("---")
st.sidebar.write("Sistema: **ONLINE ✅**")
st.sidebar.write("Motor: **Gemini 3.1**")
