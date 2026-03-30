import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURACIÓN Y SEGURIDAD (SECRETS)
# ==========================================
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ ERROR: Configura tus Secrets en Streamlit Cloud (GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY).")
    st.stop()

# ==========================================
# 2. ANIMACIÓN DE CARGA (FIRMA DE XAVIER)
# ==========================================
if 'cargado' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"<h1 style='text-align: center; color: #00FF41; font-family: monospace;'>🦾 JARVIS OS v2.0</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #888;'>PROYECTO DESARROLLADO POR: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        progreso = st.progress(0)
        for i in range(101):
            progreso.progress(i)
            time.sleep(0.01)
        st.success("✅ SISTEMA BIOMÉTRICO ONLINE")
        time.sleep(1)
    placeholder.empty()
    st.session_state.cargado = True

# ==========================================
# 3. ESTILOS VISUALES (PIZARRA PROFESIONAL)
# ==========================================
st.markdown("""
<style>
    .pizarra { background-color: #121212; border: 5px solid #3d2b1f; border-radius: 15px; padding: 25px; font-family: 'Courier New', monospace; box-shadow: 0px 10px 25px rgba(0,0,0,0.7); }
    .titulo-p { color: #00FF41; text-align: center; font-size: 22px; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px; }
    .dato { display: flex; justify-content: space-between; font-size: 19px; margin: 10px 0; color: #ffffff; }
    .val { color: #00FF41; font-weight: bold; }
    .stButton>button { width: 100%; background-color: #00FF41; color: black; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LÓGICA DE USUARIOS Y REGISTRO
# ==========================================
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Sidebar: Panel de Control
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=100)
    st.title("📂 AGENTE")
    if st.session_state.usuario:
        u = st.session_state.usuario
        st.success(f"ONLINE: {u['nombre'].upper()}")
        st.metric("Peso", f"{u['peso']} kg")
        st.metric("Meta Proteína", f"{u['meta_p']} g")
        
        # --- MODO CREADOR (Solo para Xavier) ---
        if "xavier" in u['nombre'].lower():
            st.divider()
            st.markdown("### 👑 MODO CREADOR")
            if st.button("📊 VER BASE DE DATOS"):
                try:
                    res = supabase.table('usuarios').select('*').execute()
                    st.dataframe(res.data)
                except: st.error("Error al leer base de datos.")
        
        st.divider()
        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.usuario = None
            st.rerun()

# ==========================================
# 5. PANTALLA PRINCIPAL (REGISTRO O ESCÁNER)
# ==========================================
if st.session_state.usuario is None:
    st.header("🦾 Registro de Usuario")
    with st.form("registro_form"):
        nombre_input = st.text_input("Ingresa tu nombre para el sistema:")
        peso_input = st.number_input("Tu peso actual (kg):", min_value=30.0, value=63.0)
        
        if st.form_submit_button("ACTIVAR JARVIS 🚀"):
            if nombre_input:
                meta_calc = peso_input * 2
                # Guardar en Supabase para que no se pierda
                try:
                    supabase.table('usuarios').insert({"nombre": nombre_input, "peso": peso_input, "meta_proteina": meta_calc}).execute()
                except: pass # Si ya existe o falla, ignoramos para no trabar la app
                
                st.session_state.usuario = {"nombre": nombre_input, "peso": peso_input, "meta_p": meta_calc}
                st.rerun()
            else:
                st.warning("⚠️ El nombre es obligatorio.")
else:
    # --- INTERFAZ DEL ESCÁNER ---
    st.subheader("📸 Escáner Nutricional")
    f = st.file_uploader("Sube o toma una foto de tu plato", type=["jpg", "png", "jpeg"])
    
    if f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        st.image(f, use_container_width=True, caption="Imagen cargada correctamente")
        
        if st.button("🔍 ANALIZAR AHORA"):
            with st.spinner("🤖 Jarvis Xavier procesando..."):
                try:
                    payload = {"contents": [{"parts": [
                        {"text": "Analiza la imagen y responde estrictamente en este formato: Nombre del plato|Calorías|Proteína|Carbohidratos|Grasas. Usa solo números y la unidad (ej: 20g)."},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                    ]}]}
                    r = requests.post(URL_AI, json=payload)
                    data = r.json()
                    
                    if 'candidates' in data:
                        info = data['candidates'][0]['content']['parts'][0]['text'].split('|')
                        if len(info) >= 5:
                            st.markdown(f"""
                            <div class="pizarra">
                                <div class="titulo-p">📋 ANÁLISIS: {info[0].upper()}</div>
                                <div class="dato"><span>🔥 CALORÍAS</span><span class="val">{info[1]}</span></div>
                                <div class="dato"><span>🍗 PROTEÍNA</span><span class="val">{info[2]}</span></div>
                                <div class="dato"><span>🍚 CARBOHIDRATOS</span><span class="val">{info[3]}</span></div>
                                <div class="dato"><span>🥑 GRASAS</span><span class="val">{info[4]}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.info(f"💡 Recuerda: Tu meta de hoy son **{st.session_state.usuario['meta_p']}g** de proteína.")
                    else:
                        st.error("No se pudo analizar la imagen. Intenta con otra foto.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
