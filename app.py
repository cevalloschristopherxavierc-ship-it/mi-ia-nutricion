import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core - Panel Xavier", page_icon="🦾", layout="wide")

# Estilo visual de tu captura
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
    .metric-label { font-size: 16px; color: #8b949e; }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROTOCOLO DE INICIO: PREGUNTAS (Abierto para todos) ---
st.sidebar.title("🔋 ESTADO INICIAL")
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])
    st.write(f"Sincronizando modo: {humor}")

# --- 3. PANEL DE MÉTRICAS SUPERIORES ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")

col_k, col_p, col_b = st.columns(3)
with col_k: st.markdown('<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
with col_p: st.markdown('<div class="metric-box"><p class="metric-label">🍗 Prot (g)</p><p class="metric-value">0 / 160</p></div>', unsafe_allow_html=True)
with col_b: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO MAESTRO DISCRETO (Debajo de las métricas) ---
st.markdown("---")
with st.expander("🔐 Sincronización de Privacidad"):
    master_key = st.text_input("Introduce Código Maestro para ver datos privados:", type="password")
    es_maestro = (master_key == "xavier2210")
    if es_maestro:
        st.success("✅ Acceso Maestro Confirmado. Núcleo desbloqueado.")

# --- 5. NAVEGACIÓN POR PESTAÑAS (DINÁMICA) ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "💻 DOBLE REVISIÓN", "👤 BIOMETRÍA", "📅 HORARIOS"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 HORARIOS GENERALES"])

# --- 6. FUNCIÓN DE CONEXIÓN GEMINI 3.1 ---
def analizar_con_jarvis(image_file, api_key):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    
    prompt = "Analiza esta comida. Da macros (P/C/G) y calorías. Usuario: Xavier."
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    try:
        res = requests.post(url, json=payload)
        return res.json()
    except:
        return {"error": "Fallo de conexión"}

# --- 7. CONTENIDO DE PESTAÑAS ---

with tabs[0]: # REGISTRO / PRUEBA IA
    st.subheader("📷 Escaneo de Biomasa")
    archivo = st.file_uploader("Subir foto...", type=["jpg", "png", "jpeg"])
    if archivo and "GOOGLE_API_KEY" in st.secrets:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        if st.button("ANALIZAR"):
            with st.spinner("🤖 Analizando..."):
                res = analizar_con_jarvis(img, st.secrets["GOOGLE_API_KEY"])
                if 'candidates' in res:
                    st.success(res['candidates'][0]['content']['parts'][0]['text'])

if es_maestro:
    with tabs[1]: # DOBLE REVISIÓN
        st.subheader("💻 Auditoría de Código")
        codigo_text = st.text_area("Pega código para doble revisión:", height=200)
        if st.button("🔍 REVISAR"):
            st.info("Función de auditoría lista para procesar.")

    with tabs[2]: # BIOMETRÍA
        st.subheader("👤 Datos Corporales Privados")
        st.number_input("Estatura (cm):", value=175)
        st.number_input("Peso Actual (kg):", value=75.0)

with tabs[-1]: # SIEMPRE ES HORARIOS
    st.subheader("⏰ Cronograma Portoviejo")
    st.info("- 07:00 Desayuno\n- 13:00 Almuerzo\n- 19:00 Cena")

# --- 8. BARRA
