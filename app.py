import streamlit as st
import google.generativeai as genai
from datetime import datetime
import PIL.Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Configuración de la IA con manejo de errores mejorado
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # CAMBIO CLAVE: Usamos 'models/gemini-1.5-flash' para asegurar que lo encuentre
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    else:
        st.error("⚠️ No se encontró GOOGLE_API_KEY en Secrets.")
except Exception as e:
    st.error(f"⚠️ Error de configuración: {e}")

# Memoria de Datos
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# Funciones de Tiempo
def obtener_bloque_comida():
    h = datetime.now().hour
    if 5 <= h < 12: return "Desayuno"
    elif 12 <= h < 18: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo Visual Jarvis Dark
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA ---
if not st.session_state.biometria_completada:
    st.title("👤 Biometría Profesional Jarvis")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre del Guerrero:", value="Xavier")
        u_obj = st.selectbox("Objetivo Estratégico:", ["Bajar de peso", "Subir de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 ACTIVAR NÚCLEO"):
        m_p = 12000 if u_obj == "Bajar de peso" else 8000
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "objetivo": u_obj, "meta_pasos": m_p}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (8 METAS DINÁMICAS) ---
dia_hoy = obtener_dia_actual()
regs_hoy = st.session_state.historial[dia_hoy]

tkcal = sum(r.get('k', 0) for r in regs_hoy)
tprot = sum(r.get('p', 0) for r in regs_hoy)
tcarb = sum(r.get('c', 0) for r in regs_hoy)
tgras = sum(r.get('g', 0) for r in regs_hoy)
tfibr = sum(r.get('f', 0) for r in regs_hoy)
tazuc = sum(r.get('a', 0) for r in regs_hoy)
k_quem = (st.session_state.pasos * 0.04)

m_kcal = 3000 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 2300
m_prot = int(st.session_state.u_datos['peso'] * 2.2)
m_carb = 350 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 200

st.title(f"📊 Panel Jarvis: {datetime.now().strftime('%d/%m/%Y')}")
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/{m_kcal}</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">{tprot}/{m_prot}g</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">👣 Pasos</p><p class="metric-value">{st.session_state.pasos}/{st.session_state.u_datos["meta_pasos"]}</p></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">{k_quem:.1f}</p></div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)
with col5: st.markdown(f'<div class="metric-box"><p class="metric-label">🍝 Carb</p><p class="metric-value">{tcarb}/{m_carb}g</p></div>', unsafe_allow_html=True)
with col6: st.markdown(f'<div class="metric-box"><p class="metric-label">🥑 Gras</p><p class="metric-value">{tgras}/70g</p></div>', unsafe_allow_html=True)
with col7: st.markdown(f'<div class="metric-box"><p class="metric-label">🍏 Fibr</p><p class="metric-value">{tfibr}/35g</p></div>', unsafe_allow_html=True)
with col8: st.markdown(f'<div class="metric-box"><p class="metric-label">🍭 Azuc</p><p class="metric-value">{tazuc}/50g</p></div>', unsafe_allow_html=True)

# --- 4. PESTAÑAS PRINCIPALES ---
t_ia, t_sem, t_sync = st.tabs(["🚀 REGISTRO IA", "📅 SEMANA", "🔐 SINCRONIZACIÓN"])

with t_ia:
    st.subheader("📷 Escáner Profesional")
    archivo = st.file_uploader("Sube la foto de tu plato...", type=["jpg", "png", "jpeg"])
    
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if archivo and st.button("ANALIZAR CON JARVIS"):
            img = PIL.Image.open(archivo)
            # Prompt optimizado
            prompt = "Analyze the image. Return ONLY 6 numbers separated by commas: calories, protein, carbs, fat, fiber, sugar. Example: 250, 25, 30, 8, 4, 2. No conversation."
            with st.spinner("Jarvis identificando nutrientes..."):
                try:
                    response = model.generate_content([prompt, img])
                    # Limpieza profunda de la respuesta
                    res_text = response.text.strip().replace('\n', '')
                    d = [float(x.strip()) for x in res_text.split(',')]
                    
                    bloque = obtener_bloque_comida()
                    nuevo = {"hora": datetime.now().strftime("%H:%M"), "alimento": "Plato Detectado", "bloque": bloque, "k": d[0], "p": d[1], "c": d[2], "g": d[3], "f": d[4], "a": d[5]}
                    st.session_state.historial[dia_hoy].append(nuevo)
                    st.success(f"✅ ¡Añadido! {d[0]} Kcal")
                    st.rerun()
                except Exception as e: 
                    st.error(f"Error de IA: {e}")
    
    with c_b2:
        if st.button("🗑️ BORRAR ÚLTIMO"):
            if st.session_state.historial[dia_hoy]:
                st.session_state.historial[dia_hoy].pop()
                st.warning("Último registro eliminado.")
                st.rerun()

with t_sem:
    for dia, registros in st.session_state.historial.items():
        with st.expander(f"📅 {dia}", expanded=(dia == dia_hoy)):
            if not registros: st.write("Sin datos.")
            else:
                for r in registros:
                    st.write(f"🍏 {r.get('bloque')}: {r.get('k')} Kcal - {r.get('hora')}")

with t_sync:
    st.subheader("🔐 Modo Maestro")
    pass_maestra = st.text_input("Código:", type="password")
    if pass_maestra == "xavier2210":
        st.success("Acceso Maestro")
        st.selectbox("Auditar:", ["Xavier", "Juan", "Maria"])
    elif pass_maestra: st.error("Código Incorrecto.")

# --- 5. BARRA LATERAL ---
st.sidebar.title("💧 HIDRATACIÓN")
if st.sidebar.button("➕ Añadir Vaso"): st.session_state.agua += 1
if st.sidebar.button("🔄 Reiniciar"): st.session_state.agua = 0
st.sidebar.write(f"Vasos: {st.session_state.agua}/12")
st.sidebar.markdown("---")
st.session_state.pasos = st.sidebar.number_input("👣 PASOS HOY:", value=
