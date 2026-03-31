import streamlit as st
import google.generativeai as genai
from datetime import datetime
import PIL.Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Configuración de la IA (Lee la clave que pegaste en Secrets)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Error: No se encontró la API KEY en los Secrets de Streamlit.")

# Memoria de Datos (Se mantiene igual para no perder tus funciones)
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# --- FUNCIONES DE TIEMPO ---
def obtener_bloque_comida():
    h = datetime.now().hour
    if 5 <= h < 12: return "Desayuno"
    elif 12 <= h < 18: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo Visual
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA ---
if not st.session_state.biometria_completada:
    st.title("👤 Configuración Jarvis")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_obj = st.selectbox("Objetivo:", ["Bajar de peso", "Subir de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso (kg):", value=75.0)
    
    if st.button("🚀 ACTIVAR"):
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "objetivo": u_obj, "meta_pasos": 12000}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (DINÁMICO) ---
dia_hoy = obtener_dia_actual()
regs_hoy = st.session_state.historial[dia_hoy]

# Cálculos automáticos de los registros
tkcal = sum(r.get('k', 0) for r in regs_hoy)
tprot = sum(r.get('p', 0) for r in regs_hoy)
tcarb = sum(r.get('c', 0) for r in regs_hoy)
tgras = sum(r.get('g', 0) for r in regs_hoy)
tfibr = sum(r.get('f', 0) for r in regs_hoy)
tazuc = sum(r.get('a', 0) for r in regs_hoy)

st.title(f"📊 Panel Jarvis: {datetime.now().strftime('%d/%m/%Y')}")
cols = st.columns(4)
cols[0].markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/2300</p></div>', unsafe_allow_html=True)
cols[1].markdown(f'<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">{tprot}/{int(st.session_state.u_datos["peso"]*2.2)}g</p></div>', unsafe_allow_html=True)
cols[2].markdown(f'<div class="metric-box"><p class="metric-label">🍝 Carb</p><p class="metric-value">{tcarb}/200g</p></div>', unsafe_allow_html=True)
cols[3].markdown(f'<div class="metric-box"><p class="metric-label">🥑 Gras</p><p class="metric-value">{tgras}/70g</p></div>', unsafe_allow_html=True)

# --- 4. REGISTRO IA (ANÁLISIS REAL) ---
t_ia, t_sem, t_sync = st.tabs(["🚀 REGISTRO IA", "📅 SEMANA", "🔐 SYNC"])

with t_ia:
    archivo = st.file_uploader("📷 Escanea tu comida...", type=["jpg", "png", "jpeg"])
    
    if archivo and st.button("ANALIZAR CON JARVIS"):
        img = PIL.Image.open(archivo)
        
        prompt = """Actúa como un experto en nutrición fitness. Analiza la imagen y devuelve SOLO 6 números separados por comas en este orden exacto: 
        calorías, proteínas, carbohidratos, grasas, fibra, azúcar. 
        Ejemplo si ves una manzana: 95, 0.5, 25, 0.3, 4, 19.
        No escribas texto, solo los 6 números."""
        
        with st.spinner("Jarvis identificando nutrientes..."):
            response = model.generate_content([prompt, img])
            try:
                # Convertimos la respuesta de la IA en números reales
                datos = [float(x.strip()) for x in response.text.split(',')]
                
                bloque = obtener_bloque_comida()
                nuevo = {
                    "hora": datetime.now().strftime("%H:%M"),
                    "alimento": "Plato Detectado",
                    "bloque": bloque,
                    "k": datos[0], "p": datos[1], "c": datos[2], "g": datos[3], "f": datos[4], "a": datos[5]
                }
                st.session_state.historial[dia_hoy].append(nuevo)
                st.success(f"✅ ¡Analizado! {datos[0]} kcal añadidas.")
                st.rerun()
            except:
                st.error("Hubo un problema al procesar la imagen. Intenta de nuevo.")

    if st.button("🗑️ DESHACER ÚLTIMO"):
        if st.session_state.historial[dia_hoy]:
            st.session_state.historial[dia_hoy].pop()
            st.rerun()

with t_sync:
    pass # (Aquí va tu código de xavier2210 que ya tienes)
