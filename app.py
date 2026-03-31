import streamlit as st
import google.generativeai as genai
from datetime import datetime
import PIL.Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Intentamos el 8b por ser el más estable para cuotas gratuitas
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
else:
    st.error("⚠️ Configura la API KEY en Secrets.")

# Memoria de Sesión
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# --- 2. BIOMETRÍA Y VERIFICACIÓN DE CREADOR ---
if not st.session_state.biometria_completada:
    st.title("🛡️ Activación de Núcleo Jarvis")
    col_a, col_b = st.columns(2)
    with col_a:
        u_nom = st.text_input("Nombre de Usuario:", value="Xavier")
        u_cod = st.text_input("Código de Creador (Verificación):", placeholder="Ej: J-2026")
        u_obj = st.selectbox("Objetivo:", ["Subir de peso", "Bajar de peso", "Mantener"])
    with col_b:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
        u_ver = st.checkbox("Verificación de Creador Activa")

    if st.button("🚀 INICIAR SISTEMA"):
        if u_ver:
            m_p = 12000 if u_obj == "Bajar de peso" else 8000
            st.session_state.u_datos = {
                "nombre": u_nom, "peso": u_pes, "altura": u_alt, 
                "objetivo": u_obj, "meta_pasos": m_p, "codigo": u_cod
            }
            st.session_state.biometria_completada = True
            st.success(f"Bienvenido, Comandante {u_nom}. Núcleo sincronizado.")
            st.rerun()
        else:
            st.warning("Por favor, activa la verificación de creador.")
    st.stop()

# --- 3. LÓGICA DE NOTIFICACIONES DE MACROS ---
dia_hoy = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][datetime.now().weekday()]
regs = st.session_state.historial[dia_hoy]

tkcal = sum(r.get('k', 0) for r in regs)
tprot = sum(r.get('p', 0) for r in regs)
tcarb = sum(r.get('c', 0) for r in regs)
tgras = sum(r.get('g', 0) for r in regs)

# Metas (Ajustadas a tus preferencias de hipertrofia)
m_kcal = 3000 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 2300
m_prot = int(st.session_state.u_datos['peso'] * 2.2)
m_carb = 350 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 220
m_gras = 70

# --- ALERTAS DE JARVIS ---
if tkcal > 0: # Solo si ya comió algo
    if tprot < (m_prot * 0.5): st.error(f"⚠️ ATENCIÓN: Proteína crítica ({tprot}g). Necesitas más construcción muscular.")
    if tcarb < (m_carb * 0.4): st.warning(f"⚠️ AVISO: Carbohidratos bajos ({tcarb}g). Tu energía podría bajar.")
    if tgras < 30: st.info(f"💡 NOTA: Grasas bajas. Añade grasas saludables para tus hormonas.")

# --- 4. PANEL VISUAL ---
st.title(f"🦾 Jarvis Core v2.0 - {dia_hoy}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🔥 Calorías", f"{tkcal}", f"{tkcal-m_kcal}")
c2.metric("🍗 Proteína", f"{tprot}g", f"{tprot-m_prot}g")
c3.metric("🍝 Carbs", f"{tcarb}g", f"{tcarb-m_carb}g")
c4.metric("🥑 Grasas", f"{tgras}g", f"{tgras-m_gras}g")

# --- 5. REGISTRO IA CON "PENSAMIENTO" ---
t_ia, t_hist = st.tabs(["🚀 ANALIZADOR IA", "📅 HISTORIAL"])

with t_ia:
    st.subheader("📷 Escáner de Nutrientes")
    archivo = st.file_uploader("Sube tu plato...", type=["jpg", "png", "jpeg"])
    
    if archivo and st.button("JARVIS, ANALIZA ESTO"):
        img = PIL.Image.open(archivo)
        # Pedimos los números y un consejo corto (el pensamiento de la IA)
        prompt = "Analyze image. Return 6 numbers (kcal, p, c, g, fiber, sugar) and a short 1-sentence advice in Spanish. Format: 300, 20, 30, 10, 5, 2 | Advice."
        
        with st.spinner("Jarvis está pensando..."):
            try:
                response = model.generate_content([prompt, img])
                datos_raw, consejo = response.text.split('|')
                d = [float(x.strip()) for x in datos_raw.split(',')]
                
                nuevo = {"hora": datetime.now().strftime("%H:%M"), "k": d[0], "p": d[1], "c": d[2], "g": d[3]}
                st.session_state.historial[dia_hoy].append(nuevo)
                
                st.success(f"✅ Registrado. Jarvis dice: {consejo}")
                st.balloons()
            except:
                st.error("Error de conexión. Intenta en 15 segundos.")

with t_hist:
    for d, r_list in st.session_state.historial.items():
        if r_list:
            with st.expander(f"Día {d}"):
                for r in r_list:
                    st.write(f"🍴 {r['hora']} - {r['k']} Kcal (P:{r['p']}g, C:{r['c']}g)")

# --- SIDEBAR (AGUA Y PASOS) ---
st.sidebar.title("💧 HIDRATACIÓN")
if st.sidebar.button("🥤 Beber Vaso"): st.session_state.agua += 1
st.sidebar.progress(min(st.session_state.agua/12, 1.0))
st.sidebar.write(f"Vasos: {st.session_state.agua}/12")

st.sidebar.markdown("---")
st.sidebar.title("👣 ACTIVIDAD")
st.session_state.pasos = st.sidebar.number_input("Pasos hoy:", value=st.session_state.pasos, step=500)
