import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# 1. SEGURIDAD
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Error en Secrets.")
    st.stop()

# --- ANIMACIÓN DE CARGA OBLIGATORIA ---
if 'first_run' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"<h2 style='text-align: center; color: #00FF41; font-family: monospace;'>🦾 JARVIS OS</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #888;'>PROYECTO BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            bar.progress(i)
            time.sleep(0.015)
        st.success("SISTEMA ONLINE")
        time.sleep(0.8)
    placeholder.empty()
    st.session_state.first_run = True

# --- DISEÑO PIZARRA ---
st.markdown("""
<style>
    .pizarra { background-color: #121212; border: 4px solid #3d2b1f; border-radius: 12px; padding: 20px; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-size: 20px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .dato { display: flex; justify-content: space-between; font-size: 18px; margin: 8px 0; color: #fff; }
    .val { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("📂 Perfil")
    if st.session_state.usuario:
        u = st.session_state.usuario
        st.write(f"🚀 **Agente: {u['nombre'].upper()}**")
        st.write(f"⚖️ Peso: {u['peso']}kg")
        
        # EL MODO ADMIN (Cualquier nombre que contenga 'xavier')
        if "xavier" in u['nombre'].lower():
            st.divider()
            st.markdown("### 👑 MODO CREADOR")
            if st.button("📊 Ver Base de Datos"):
                res = supabase.table('usuarios').select('*').execute()
                st.dataframe(res.data)
        
        if st.button("🚪 Salir"):
            st.session_state.clear()
            st.rerun()

# --- APP ---
if not st.session_state.usuario:
    st.header("🦾 Bienvenido a Jarvis")
    with st.form("registro"):
        nombre = st.text_input("Tu nombre")
        peso = st.number_input("Peso (kg)", min_value=30.0, value=63.0)
        if st.form_submit_button("INICIAR SESIÓN"):
            if nombre:
                meta = peso * 2
                # Registro en base de datos
                supabase.table('usuarios').insert({"nombre": nombre, "peso": peso, "meta_proteina": meta}).execute()
                st.session_state.usuario = {"nombre": nombre, "peso": peso, "meta_p": meta}
                st.rerun()
else:
    f = st.file_uploader("📸 Escanea tu plato", type=["jpg", "png", "jpeg"])
    if f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        st.image(f, use_container_width=True)
        if st.button("🔍 ANALIZAR NUTRIENTES"):
            with st.spinner("🤖 Jarvis calculando..."):
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
                        <div class="titulo-p">📋 {res[0].upper()}</div>
                        <div class="dato"><span>🔥 CALORÍAS</span><span class="val">{res[1]}</span></div>
                        <div class="dato"><span>🍗 PROTEÍNA</span><span class="val">{res[2]}</span></div>
                        <div class="dato"><span>🍚 CARBOS</span><span class="val">{res[3]}</span></div>
                        <div class="dato"><span>🥑 GRASAS</span><span class="val">{res[4]}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
