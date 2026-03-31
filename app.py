import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Memoria de sesión (Bucle Semanal)
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# Lógica de Horarios (Desayuno, Merienda, Cena)
def obtener_bloque_comida():
    hora = datetime.now().hour
    if 6 <= hora < 12: return "Desayuno"
    elif 12 <= hora < 17: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual de tu captura (Premium Dark)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 13px; color: #8b949e; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. IDENTIFICACIÓN Y BIOMETRÍA PROFESIONAL (AL INICIO) ---
if not st.session_state.biometria_completada:
    st.title("👤 Identificación y Biometría Profesional")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_eda = st.number_input("Edad:", value=20)
        u_obj = st.selectbox("Objetivo Físico:", ["Subir de peso (Volumen)", "Bajar de peso (Definición)", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 INICIAR SISTEMA"):
        # Lógica de pasos: Más peso o definición = más pasos necesarios
        meta_pasos = 12000 if u_obj == "Bajar de peso (Definición)" else 8000
        st.session_state.u_datos = {
            "nombre": u_nom, "peso": u_pes, "altura": u_alt, 
            "objetivo": u_obj, "meta_pasos": meta_pasos
        }
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (31/03/2026) ---
st.sidebar.title("🔋 ESTADO")
with st.sidebar.expander("📝 Reporte", expanded=True):
    st.select_slider("Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    if st.button("🔄 Repetir Biometría"):
        st.session_state.biometria_completada = False
        st.rerun()

st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
dia_hoy = obtener_dia_actual()

# CÁLCULOS PARA EL PANEL (Suma real de escaneos)
regs_hoy = st.session_state.historial[dia_hoy]
total_kcal = sum(r.get('kcal_n', 0) for r in regs_hoy)
total_prot = sum(r.get('prot_n', 0) for r in regs_hoy)
kcal_quemadas = (st.session_state.pasos * 0.04)
meta_kcal = 3000 if st.session_state.u_datos['objetivo'] == "Subir de peso (Volumen)" else 2300

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal Consumidas</p><p class="metric-value">{total_kcal} / {meta_kcal}</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">{total_prot}g / 160g</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">👣 Pasos</p><p class="metric-value">{st.session_state.pasos} / {st.session_state.u_datos["meta_pasos"]}</p></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-box"><p class="metric-label">🏃 Quemado Aprox</p><p class="metric-value">{kcal_quemadas:.1f} kcal</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO MAESTRO ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización"):
    if st.text_input("Código:", type="password") == "xavier2210": es_maestro = True

# --- 5. PESTAÑAS ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL", "👥 PANEL CREADOR", "💻 REVISIÓN"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 REGISTRO SEMANAL"])

# --- 6. FUNCIÓN DE ESCANEO (SUMA AUTOMÁTICA) ---
def analizar_y_sumar(img, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    prompt = """Analiza el alimento. Responde en este formato:
    Nombre: [Nombre Alimento]
    Kcal: [Solo numero]
    Proteina: [Solo numero]
    Detalle: [Peso y nutrientes brevemente]"""
    
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        texto = res['candidates'][0]['content']['parts'][0]['text']
        
        # Extraer números para el Panel en vivo
        lineas = texto.split('\n')
        kcal_val, prot_val, nombre_alim = 0, 0, "Alimento"
        for l in lineas:
            if "Kcal:" in l: kcal_val = int(''.join(filter(str.isdigit, l)))
            if "Proteina:" in l: prot_val = int(''.join(filter(str.isdigit, l)))
            if "Nombre:" in l: nombre_alim = l.split(":")[1].strip()

        bloque = obtener_bloque_comida()
        nuevo = {
            "hora": datetime.now().strftime("%H:%M"), "alimento": nombre_alim, 
            "bloque": bloque, "detalle_completo": texto,
            "kcal_n": kcal_val, "prot_n": prot_val
        }
        st.session_state.historial[dia_hoy].append(nuevo)
        return texto
    except: return "Error en escaneo."

# --- 7. CONTENIDO ---
with tabs[0]:
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Subir plato...", type=["jpg", "png", "jpeg"])
    if archivo and st.button("ANALIZAR Y GUARDAR"):
        res = analizar_y_sumar(Image.open(archivo), st.secrets["GOOGLE_API_KEY"])
        st.success("Analizado. Datos sumados al Panel de Control.")

with tabs[1]: # REGISTRO SEMANAL LIMPIO (NOMBRE + BOTÓN)
    st.subheader("📅 Registro Semanal")
    for dia, regs in st.session_state.historial.items():
        with st.expander(f"📍 {dia}", expanded=(dia == dia_hoy)):
            for b in ["Desayuno", "Merienda", "Cena"]:
                st.markdown(f"**--- {b} ---**")
                comidas = [r for r in regs if r.get('bloque') == b]
                if comidas:
                    for i, c in enumerate(comidas):
                        col_it, col_bt = st.columns([3, 1])
                        col_it.write(f"🍏 {c['alimento']} ({c['hora']})")
                        if col_bt.button("Detalles", key=f"btn_{dia}_{b}_{i}"):
                            st.info(c['detalle_completo'])
                else: st.write("Sin registros.")

if es_maestro:
    with tabs[2]: # PANEL CREADOR
        st.subheader("👥 Supervisión de Discípulos")
        st.write(f"Viendo datos de: **{st.session_state.u_datos['nombre']}**")
        st.json(st.session_state.historial)

# --- 8. CONTROLES LATERALES ---
st.sidebar.markdown("---")
if st.sidebar.button("➕ Vaso de Agua"): st.session_state.agua += 1
st.sidebar.write(f"💧 Agua: {st.session_state.agua}/12")

st.sidebar.markdown("---")
st.session_state.pasos = st.sidebar.number_input("👣 Pasos Caminados:", min_value=0, value=st.session_state.pasos, step=500)
