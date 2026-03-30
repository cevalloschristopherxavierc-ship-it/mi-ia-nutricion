import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIG & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Nutrición Pro", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
exceptException as e:
    st.error(f"⚠️ Error Crítico en Secrets: {e}. Revisa Streamlit Cloud.")
    st.stop()

# --- 2. SESSION STATE ---
for k in ['k_t', 'p_t', 'c_t', 'g_t']:
    if k not in st.session_state: st.session_state[k] = 0.0

# --- 3. SIDEBAR (PERFIL XAVIER) ---
with st.sidebar:
    st.title("🦾 PERFIL JARVIS")
    u_nom = st.text_input("Nombre:", "Xavier")
    u_pes = st.number_input("Peso Actual (kg):", 63.0)
    u_alt = st.number_input("Altura (cm):", 170)
    u_eda = st.number_input("Edad:", 20)
    u_act = st.selectbox("Actividad Principal:", ["Fútbol 2h (Portoviejo)", "Hipertrofia Glúteos/Piernas"])
    meta_k = st.number_input("Meta Kcal Diaria:", 2500)
    
    st.divider()
    prog = min(st.session_state.k_t / meta_k, 1.0)
    st.write(f"🔥 Progreso Hoy: {int(prog*100)}%")
    st.progress(prog)
    st.write(f"Consumido: {int(st.session_state.k_t)} / {meta_k} kcal")
    
    if st.button("🔄 Reiniciar Contador Hoy"):
        for k in ['k_t', 'p_t', 'c_t', 'g_t']: st.session_state[k] = 0.0
        st.rerun()

# --- 4. PANEL PRINCIPAL ---
st.title(f"📈 Dashboard Nutricional: {u_nom}")
t1, t2 = st.tabs(["📊 PROGRESO DIARIO", "🍽️ REGISTRAR COMIDA"])

with t1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    col2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    col3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    df_m = pd.DataFrame({'M':['Prot','Carb','Gras'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    st.plotly_chart(px.pie(df_m, values='G', names='M', hole=0.5, template="plotly_dark", 
                          color_discrete_sequence=['#00FF41','#FFC107','#2196F3']), use_container_width=True)

with t2:
    col_f, col_m = st.columns(2)
    res_c = None

    with col_f:
        st.subheader("📸 Análisis por Foto")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"], key="camara")
        if foto and st.button("🔍 ESCANEAR CON IA"):
            with st.spinner("🤖 Jarvis analizando ración..."):
                try:
                    img_b64 = base64.b64encode(foto.read()).decode()
                    # Prompt blindado
                    prompt = f"Usuario {u_pes}kg, {u_alt}cm. Actividad: {u_act}. Analiza foto y responde SOLO en este formato numérico estricto: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    
                    # MEJORA: Depuración de errores de la API de Google
                    if 'error' in r:
                        st.error(f"❌ Error API Gemini: Revisa tu API Key en Secrets o si Google está saturado. Detalle: {r['error']['message']}")
                    else:
                        raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                        # Limpieza profunda
                        clean = raw.replace(' ','').replace('g','').replace('kcal','').replace('*','').replace('\n','')
                        parts = clean.split('|')
                        
                        if len(parts) >= 5:
                            res_c = {"n":parts[0], "k":float(parts[1]), "p":float(parts[2]), "c":float(parts[3]), "g":float(parts[4])}
                        else:
                            st.error(f"⚠️ Formato IA incorrecto. Recibido: {raw}. Prueba registro manual.")
                except Exception as e:
                    st.error(f"❌ Error de Conexión IA: {e}")

    with col_m:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_entry_f"):
            n_m = st.text_input("Nombre del Plato:")
            col1, col2 = st.columns(2)
            k_m = col1.number_input("Kcal:", min_value=0.0, value=500.0)
            p_m = col2.number_input("Proteína (g):", min_value=0.0, value=30.0)
            c_m = col1.number_input("Carbos (g):", min_value=0.0, value=50.0)
            g_m = col2.number_input("Grasas (g):", min_value=0.0, value=15.0)
            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                if n_m: res_c = {"n":n_m, "k":k_m, "p":p_m, "c":c_m, "g":g_m}

    if res_c:
        # Actualización de estados inmediata
        st.session_state.k_t += res_c['k']
        st.session_state.p_t += res_c['p']
        st.session_state.c_t += res_c['c']
        st.session_state.g_t += res_c['g']
        try:
            supabase.table('registros_comida').insert({
                "usuario": u_nom, "comida": res_c['n'], "kcal": res_c['k'],
                "proteina": res_c['p'], "carbos": res_c['c'], "grasas": res_c['g']
            }).execute()
            st.success(f"✅ ¡{res_c['n']} registrado!")
        exceptException as db_e:
            st.warning(f"⚠️ Registrado en sesión, pero no en base de datos. Error: {db_e}")
        
        # Pizarra Visual
        st.markdown(f"""
        <div style="background:#1a1a1a; border:2px solid #59402a; border-radius:10px; padding:15px; color:white; font-family:monospace; text-align:center;">
            <div style="font-weight:bold; color:#00FF41; margin-bottom:10px; text-transform:uppercase;">{res_c['n']}</div>
            <div style="display:flex; justify-content:space-around; font-size:18px;">
                <div>🔥<br>{res_c['k']:.0f}<br>Kcal</div>
                <div>🍗<br>{res_c['p']:.1f}g<br>Prot</div>
                <div>🍚<br>{res_c['c']:.1f}g<br>Carb</div>
                <div>🥑<br>{res_c['g']:.1f}g<br>Gras</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.rerun()

st.divider()
try:
    hist = supabase.table('registros_comida').select('*').order('created_at', desc=True).limit(5).execute()
    for r in hist.data:
        st.write(f"🍴 **{r['comida']}**: {r['kcal']}kcal | P:{r['proteina']}g C:{r['carbos']}g G:{r['grasas']}g")
except:
    st.info("Registra tu primera comida para ver el historial.")
