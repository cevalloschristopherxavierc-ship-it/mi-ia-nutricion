import streamlit as st
import requests
import base64
from PIL import Image
import io
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Lógica de Reinicio Diario (Agua y Pasos)
if 'ultima_fecha' not in st.session_state:
    st.session_state.ultima_fecha = datetime.now().date()

if st.session_state.ultima_fecha != datetime.now().date():
    st.session_state.agua = 0
    st.session_state.pasos = 0
    st.session_state.ultima_fecha = datetime.now().date()

# Memoria de historial y biometría
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

def obtener_bloque_comida():
    h = datetime.now().hour
    if 6 <= h < 12: return "Desayuno"
    elif 12 <= h < 17: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 12px; color: #8b949e; text-transform: uppercase; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA Y OBJETIVO ---
if not st.session_state.biometria_completada:
    st.title("👤 Configuración de Perfil Profesional")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_eda = st.number_input("Edad:", value=20)
        u_obj = st.selectbox("Objetivo:", ["Bajar de peso", "Subir de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 ACTIVAR JARVIS"):
        meta_p = 12000 if u_obj == "Bajar de peso" else 8000
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "objetivo": u_obj, "meta_pasos": meta_p}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (CON TODAS LAS METAS) ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
dia_hoy = obtener_dia_actual()
regs_hoy = st.session_state.historial[dia_hoy]

# Sumar nutrientes registrados hoy
tkcal = sum(r.get('k', 0) for r in regs_hoy)
tprot = sum(r.get('p', 0) for r in regs_hoy)
tcarb = sum(r.get('c', 0) for r in regs_hoy)
tgras = sum(r.get('g', 0) for r in regs_hoy)
tfibr = sum(r.get('f', 0) for r in regs_hoy)
tazuc = sum(r.get('a', 0) for r in regs_hoy)
k_quem = (st.session_state.pasos * 0.04)

# Metas dinámicas
m_kcal = 3000 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 2300
m_carb = 350 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 200
m_gras = 80 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 60

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/{m_kcal}</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">{tprot}g/160g</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">👣 Pasos</p><p class="metric-value">{st.session_state.pasos}/{st.session_state.u_datos["meta_pasos"]}</p></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">{k_quem:.1f} kcal</p></div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)
with col5: st.markdown(f'<div class="metric-box"><p class="metric-label">🍝 Carbos</p><p class="metric-value">{tcarb}g/{m_carb}g</p></div>', unsafe_allow_html=True)
with col6: st.markdown(f'<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">{tgras}g/{m_gras}g</p></div>', unsafe_allow_html=True)
with col7: st.markdown(f'<div class="metric-box"><p class="metric-label">🍏 Fibra</p><p class="metric-value">{tfibr}g/35g</p></div>', unsafe_allow_html=True)
with col8: st.markdown(f'<div class="metric-box"><p class="metric-label">🍭 Azúcar</p><p class="metric-value">{tazuc}g/50g</p></div>', unsafe_allow_html=True)

# --- 4. PESTAÑAS (REGISTRO SEMANAL Y SINCRONIZACIÓN LADO A LADO) ---
t_ia, t_sem, t_sync = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL", "🔐 SINCRONIZACIÓN"])

with t_ia:
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Subir foto...", type=["jpg", "png", "jpeg"])
    if archivo and st.button("ANALIZAR Y SUMAR"):
        # Lógica de simulación para prueba inmediata
        nuevo = {"hora": datetime.now().strftime("%H:%M"), "alimento": "Comida Detectada", "bloque": obtener_bloque_comida(), 
                 "detalle": "Kcal: 150 | Prot: 15 | Carb: 20 | Gras: 5 | Fibra: 3 | Azucar: 2", "k": 150, "p": 15, "c": 20, "g": 5, "f": 3, "a": 2}
        st.session_state.historial[dia_hoy].append(nuevo)
        st.success("Analizado. Datos inyectados al Panel.")

with t_sem:
    st.subheader("📅 Historial de la Semana")
    for dia, registros in st.session_state.historial.items():
        with st.expander(f"📍 {dia}", expanded=(dia == dia_hoy)):
            for b in ["Desayuno", "Merienda", "Cena"]:
                items = [r for r in registros if r.get('bloque') == b]
                if items:
                    for i, it in enumerate(items):
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"🍏 {it['alimento']} ({it['hora']})")
                        if c2.button("Detalles", key=f"det_{dia}_{b}_{i}"): st.info(it['detalle'])

with t_sync:
    st.subheader("🔐 Panel Maestro de Perfiles")
    cod_m = st.text_input("Ingresa Código de Creador:", type="password")
    if cod_m == "xavier2210":
        st.success("Acceso Maestro Confirmado")
        disc_sel = st.selectbox("Auditar Perfil:", ["Xavier (Principal)", "Juan (ID-002)", "Maria (ID-003)"])
        st.write(f"Viendo datos de: **{disc_sel}**")
        if "Juan" in disc_sel:
            st.warning("Perfil de Juan: Peso 82kg | Meta 12k pasos | Último registro: Pollo (14:30)")
    elif cod_m != "":
        st.error("Código incorrecto.")

# --- 5. LATERAL (AGUA Y PASOS) ---
st.sidebar.title("💧 HIDRATACIÓN")
ca1, ca2 = st.sidebar.columns(2)
if ca1.button("➕ Añadir"): st.session_state.agua += 1
if ca2.button("🔄 Reset"): st.session_state.agua = 0
st.sidebar.write(f"Vasos hoy: {st.session_state.agua}/12")
st.sidebar.markdown("---")
st.session_state.pasos = st.sidebar.number_input("👣 PASOS HOY:", min_value=0, value=st.session_state.pasos, step=500)
