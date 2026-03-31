import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core v4", page_icon="🦾", layout="wide")

# Inicializar base de datos temporal en la sesión
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; }
    .metric-label { font-size: 14px; color: #8b949e; }
    .metric-value { font-size: 20px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PREGUNTAS DEL INICIO (PROHIBIDO CAMBIAR) ---
st.sidebar.title("🔋 PROTOCOLO DE ACCESO")
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia = st.select_slider("Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor = st.selectbox("Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])
    if st.button("🔄 Resetear Estado"): st.rerun()

with st.sidebar.expander("📏 Biometría Xavier", expanded=True):
    estatura = st.number_input("Estatura (cm):", value=175)
    peso = st.number_input("Peso (kg):", value=75.0)
    if st.button("🔄 Corregir Datos"): st.rerun()

# --- 3. PANEL DE CONTROL: MÉTRICAS ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
dia_hoy = obtener_dia_actual()
st.subheader(f"Hoy es {dia_hoy}")

# Cálculo de totales del día actual para las métricas
hoy_registros = st.session_state.historial[dia_hoy]
total_kcal = sum(r.get('kcal', 0) for r in hoy_registros)
total_prot = sum(r.get('prot', 0) for r in hoy_registros)

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal Consumidas</p><p class="metric-value">{total_kcal} / 2800</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Proteína Total</p><p class="metric-value">{total_prot}g / 160g</p></div>', unsafe_allow_html=True)
with c3:
    progreso_agua = min(st.session_state.agua / 12, 1.0)
    st.markdown('<div class="metric-box"><p class="metric-label">💧 Hidratación</p></div>', unsafe_allow_html=True)
    st.progress(progreso_agua, text=f"{st.session_state.agua} / 12 vasos")

# --- 4. ACCESO DISCRETO ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización"): # Borrado xavier2210 como pediste
    master_key = st.text_input("Código Maestro:", type="password")
    if master_key == "xavier2210":
        es_maestro = True
        st.success("Acceso Creador Activado.")

# --- 5. PESTAÑAS ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "📅 HORARIO SEMANAL", "🛠️ CREADOR", "💻 DOBLE REVISIÓN"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 HORARIOS GENERALES"])

# --- 6. FUNCIÓN IA (CON REGISTRO) ---
def analizar_y_guardar(image_file, api_key):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    
    # Prompt con los datos específicos que pediste
    prompt = """Analiza la imagen y devuelve EXACTAMENTE este formato:
    Calorías: [valor]
    Carbohidratos: [valor]
    Azúcares (Fructosa): [valor]
    Fibra: [valor]
    Proteína: [valor]
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    res = requests.post(url, json=payload).json()
    
    if 'candidates' in res:
        texto = res['candidates'][0]['content']['parts'][0]['text']
        # Lógica simple de guardado (simulada para el historial)
        nuevo_registro = {"hora": datetime.now().strftime("%H:%M"), "detalle": texto, "kcal": 0, "prot": 0}
        st.session_state.historial[dia_hoy].append(nuevo_registro)
        return texto
    return "Error en escaneo."

# --- 7. CONTENIDO DE PESTAÑAS ---
with tabs[0]:
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Capturar biomasa...", type=["jpg", "png", "jpeg"])
    if archivo and "GOOGLE_API_KEY" in st.secrets:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        if st.button("ANALIZAR Y REGISTRAR"):
            resultado = analizar_y_guardar(img, st.secrets["GOOGLE_API_KEY"])
            st.success(resultado)

with tabs[1]: # EL HORARIO EN BUCLE
    st.subheader("📅 Horario y Comidas de la Semana")
    for dia, registros in st.session_state.historial.items():
        with st.expander(f"📍 {dia}", expanded=(dia == dia_hoy)):
            if not registros:
                st.write("Sin registros aún.")
            for r in registros:
                st.info(f"**{r['hora']}** - {r['detalle']}")

if es_maestro:
    with tabs[2]: # APARTADO DE CREADOR
        st.subheader("🛠️ Panel del Creador (Admin)")
        st.write("Aquí puedes ver todos los registros crudos del sistema.")
        st.json(st.session_state.historial)
        if st.button("🗑️ Limpiar historial semanal"):
            st.session_state.historial = {dia: [] for dia in st.session_state.historial}
            st.rerun()

# --- 8. HIDRATACIÓN LATERAL ---
st.sidebar.markdown("---")
if st.sidebar.button("➕ Beber Agua"):
    st.session_state.agua += 1
    st.rerun()
