import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Nutrición Pro", layout="wide")

# --- 2. CONEXIÓN (SECRETS) ---
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error(f"⚠️ Error en Secrets o Supabase. Revisa la configuración. Detalle: {e}")
    st.stop()

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .pizarra { background-color: #1a1a1a; border: 4px solid #59402a; border-radius: 15px; padding: 20px; color: white; font-family: monospace; margin: 10px 0; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 1px solid #333; margin-bottom: 15px; text-transform: uppercase; }
    .verde { color: #00FF41; font-weight: bold; }
    .macro-box { text-align: center; background: #262626; padding: 10px; border-radius: 10px; border: 1px solid #444; width: 22%; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

# --- 4. INICIALIZAR SESIÓN ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0
if 'prot' not in st.session_state: st.session_state.prot = 0.0
if 'carb' not in st.session_state: st.session_state.carb = 0.0
if 'gras' not in st.session_state: st.session_state.gras = 0.0

# --- 5. SIDEBAR: PERFIL COMPLETO (SISTEMA NUEVO) ---
with st.sidebar:
    st.title("🦾 PERFIL JARVIS")
    st.info("Configura tus datos de atleta:")
    u_nom = st.text_input("Nombre:", value="Xavier")
    u_pes = st.number_input("Peso Actual (kg):", value=63.0, step=0.1)
    u_alt = st.number_input("Estatura (cm):", value=170, step=1)
    u_eda = st.number_input("Edad:", value=20, step=1)
    
    # Campo de fútbol o gym
    u_act = st.selectbox("Actividad Principal:", ["Fútbol (2h Portoviejo)", "Hipertrofia (Gym)"])
    
    meta_diaria = st.number_input("Meta Kcal Diaria:", value=2500)
    
    st.divider()
    prog = min(st.session_state.kcal_total / meta_diaria, 1.0)
    st.write(f"🔥 Progreso Hoy: {int(prog * 100)}%")
    st.progress(prog)
    st.write(f"Consumido: {int(st.session_state.kcal_total)} / {int(meta_diaria)} kcal")
    
    if st.button("🔄 Reiniciar Día"):
        st.session_state.kcal_total = st.session_state.prot = st.session_state.carb = st.session_state.gras = 0.0
        st.rerun()

# --- 6. PANEL PRINCIPAL ---
st.title(f"📈 Dashboard Nutricional: {u_nom}")
t1, t2 = st.tabs(["📊 PROGRESO", "🍽️ REGISTRAR COMIDA"])

with t1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Proteína Total", f"{st.session_state.prot:.1f} g")
    col2.metric("Carbos Total", f"{st.session_state.carb:.1f} g")
    col3.metric("Grasas Total", f"{st.session_state.gras:.1f} g")
    
    # Gráfica de Macros del Día
    df_m = pd.DataFrame({
        'Nutriente': ['Proteína', 'Carbos', 'Grasas'],
        'Gramos': [st.session_state.prot, st.session_state.carb, st.session_state.gras]
    })
    st.plotly_chart(px.pie(df_m, values='Gramos', names='Nutriente', hole=0.5, template="plotly_dark", 
                          title="Desglose de Macros de Hoy", color_discrete_sequence=['#00FF41', '#FFC107', '#2196F3']), use_container_width=True)

with t2:
    c_foto, c_manual = st.columns(2)
    comida_data = None

    with c_foto:
        st.subheader("📸 Escaneo por Foto")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"], key="camara")
        if foto:
            img_b64 = base64.b64encode(foto.read()).decode('utf-8')
            st.image(foto, width=220)
            if st.button("🔍 ANALIZAR NUTRIENTES"):
                with st.spinner("🤖 Jarvis analizando biometría y porción..."):
                    # MEJORA CLAVE: Enviar contexto completo de Xavier a la IA
                    instruccion_ia = f"""
                    Analiza esta foto de comida. Soy Xavier, peso {u_pes}kg, mido {u_alt}cm, tengo {u_eda} años y mi actividad es {u_act}.
                    Responde estrictamente en este formato numérico: Nombre|Kcal|Prot|Carb|Gras
                    No añadas texto adicional.
                    """
                    pld = {"contents": [{"parts": [{"text": instruccion_ia}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
                    try:
                        r = requests.post(URL_AI, json=pld).json()
                        res = r['candidates'][0]['content']['parts'][0]['text'].strip().split('|')
                        comida_data = {"n": res[0], "k": float(res[1]), "p": float(res[2]), "c": float(res[3]), "g": float(res[4])}
                    except: st.error("❌ Error en la IA. Revisa si el plato es visible o usa el registro manual.")

    with c_manual:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_entry_form"):
            fn = st.text_input("Nombre del plato:")
            fk = st.number_input("Kcal estimadas:", min_value=0.0)
            fp = st.number_input("Proteína (g):", min_value=0.0)
            fc = st.number_input("Carbos (g):", min_value=0.0)
            fg = st.number_input("Grasas (g):", min_value=0.0)
            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                if fn:
                    comida_data = {"n": fn, "k": fk, "p": fp, "c": fc, "g": fg}
                else:
                    st.warning("Escribe el nombre del plato.")

    # --- PROCESAMIENTO Y ACTUALIZACIÓN DE SESIÓN ---
    if comida_data:
        # Sumar a la sesión actual inmediatamente
        st.session_state.kcal_total += comida_data['k']
        st.session_state.prot += comida_data['p']
        st.session_state.carb += comida_data['c']
        st.session_state.gras += comida_data['g']
        
        # Guardar en Supabase
        try:
            supabase.table('registros_comida').insert({
