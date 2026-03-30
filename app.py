import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# 1. SEGURIDAD (Tus Secrets que ya configuraste)
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Error en Secrets. Revisa Streamlit Cloud.")
    st.stop()

# --- ANIMACIÓN DE CARGA INICIAL (Firma de Xavier) ---
if 'loading' not in st.session_state:
    msg = st.empty()
    bar = st.progress(0)
    for i in range(101):
        # Aquí corregí el nombre a Xavier
        msg.markdown(f"<h3 style='text-align: center; color: #00FF41;'>🚀 INICIANDO JARVIS BY: XAVIER CEVALLOS... {i}%</h3>", unsafe_allow_html=True)
        bar.progress(i)
        time.sleep(0.01) # Un poco más rápido para no esperar tanto
    time.sleep(0.5)
    msg.empty()
    bar.empty()
    st.session_state.loading = True

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
    .pizarra { background-color: #121212; border: 5px solid #3d2b1f; border-radius: 15px; padding: 25px; font-family: 'Courier New', monospace; }
    .titulo { color: #00FF41; text-align: center; font-size: 24px; border-bottom: 1px solid #333; padding-bottom: 10px; }
    .dato { display: flex; justify-content: space-between; font-size: 20px; margin: 12px 0; color: #fff; }
    .val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE USUARIOS ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

with st.sidebar:
    st.title("👤 Perfil")
    if st.session_state.usuario:
        u = st.session_state.usuario
        st.write(f"**Hola, {u['nombre']}!**")
        st.write(f"⚖️ Peso: {u['peso']}kg")
        
        # EL MODO ADMIN (Solo para Xavier)
        if "xavier" in u['nombre'].lower():
            st.divider()
            st.markdown("### 👑 MODO CREADOR")
            if st.button("📊 Ver Base de Datos"):
                res = supabase.table('usuarios').select('*').execute()
                st.write(f"Usuarios totales: {len(res.data)}")
                st.dataframe(res.data) # Solo tú puedes ver la lista de quién usa tu app
        
        if st.button("🚪 Salir"):
            st.session_state.usuario = None
            st.rerun()

# --- INTERFAZ PRINCIPAL ---
if not st.session_state.usuario:
    st.header("🦾 Jarvis Nutrición")
    with st.form("registro"):
        nombre = st.text_input("Ingresa tu nombre")
        peso = st.number_input("Peso (kg)", min_value=30.0, value=70.0)
        if st.form_submit_button("ENTRAR AL SISTEMA"):
            if nombre:
                meta = peso * 2
                data = {"nombre": nombre, "peso": peso, "meta_proteina": meta}
                # Guardar en Supabase
                supabase.table('usuarios').insert(data).execute()
                st.session_state.usuario = {"nombre": nombre, "peso": peso, "meta_p": meta}
                st.rerun()
else:
    # ESCÁNER DE COMIDA
    f = st.file_uploader("📸 Escanea tu plato", type=["jpg", "jpeg", "png"])
    if f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        st.image(f, use_container_width=True)
        if st.button("🔍 ANALIZAR NUTRIENTES"):
            with st.spinner("🤖 Jarvis Xavier calculando..."):
                payload = {"contents": [{"parts": [
                    {"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                ]}]}
                r = requests.post(URL_AI, json=payload)
                data = r.json()
                if 'candidates' in data:
                    res = data['candidates'][0]['content']['parts'][0]['text'].split('|')
                    st.markdown(f"""
                    <div class="pizarra">
                        <div class="titulo">📋 {res[0].upper()}</div>
                        <div class="dato"><span>🔥 CALORÍAS</span><span class="val">{res[1]}</span></div>
                        <div class="dato"><span>🍗 PROTEÍNA</span><span class="val">{res[2]}</span></div>
                        <div class="dato"><span>🍚 CARBOS</span><span class="val">{res[3]}</span></div>
                        <div class="dato"><span>🥑 GRASAS</span><span class="val">{res[4]}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
