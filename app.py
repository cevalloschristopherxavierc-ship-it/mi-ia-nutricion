import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIG & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. SESSION STATE ---
for k in ['k_t', 'p_t', 'c_t', 'g_t']:
    if k not in st.session_state: st.session_state[k] = 0.0

# --- 3. SIDEBAR (PERFIL XAVIER / USUARIO NUEVO) ---
with st.sidebar:
    st.title("🦾 PERFIL JARVIS")
    u_nom = st.text_input("Nombre:", "Xavier")
    u_pes = st.number_input("Peso (kg):", 63.0)
    u_alt = st.number_input("Altura (cm):", 170)
    u_eda = st.number_input("Edad:", 20)
    u_act = st.selectbox("Actividad:", ["Fútbol 2h", "Hipertrofia", "Gym"])
    meta_k = st.number_input("Meta Kcal Diaria:", 2500)
    
    st.divider()
    prog = min(st.session_state.k_t / meta_k, 1.0)
    st.write(f"🔥 Progreso: {int(prog*100)}%")
    st.progress(prog)
    if st.button("🔄 Reiniciar Día"):
        for k in ['k_t', 'p_t', 'c_t', 'g_t']: st.session_state[k] = 0.0
        st.rerun()

# --- 4. PANEL PRINCIPAL ---
st.title(f"📈 Dashboard: {u_nom}")
t1, t2 = st.tabs(["📊 PROGRESO", "🍽️ REGISTRAR"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    df_m = pd.DataFrame({'M':['Prot','Carb','Gras'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    st.plotly_chart(px.pie(df_m, values='G', names='M', hole=0.5, template="plotly_dark", color_discrete_sequence=['#00FF41','#FFC107','#2196F3']), use_container_width=True)

with t2:
    col_f, col_m = st.columns(2)
    res_c = None

    with col_f:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR PLATO"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_b64 = base64.b64encode(foto.read()).decode()
                    prompt = f"Usuario {u_pes}kg, {u_alt}cm. Analiza foto y responde SOLO: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    
                    # Extracción segura de texto
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    # Limpiamos todo lo que no sea número o barras
                    clean = raw.replace(' ','').replace('g','').replace('kcal','').replace('*','')
                    parts = clean.split('|')
                    
                    if len(parts) >= 5:
                        res_c = {"n":parts[0], "k":float(parts[1]), "p":float(parts[2]), "c":float(parts[3]), "g":float(parts[4])}
                    else:
                        st.error(f"⚠️ Formato IA incorrecto. Recibido: {raw}")
                except Exception as e:
                    st.error(f"❌ Error de Conexión: {e}")

    with col_m:
        st.subheader("✍️ Registro Manual")
        with st.form("f_man"):
            n_m = st.text_input("Nombre del Plato")
            k_m = st.number_input("Kcal", 0.0)
            p_m = st.number_input("Proteína (g)", 0.0)
            c_m = st.number_input("Carbos (g)", 0.0)
            g_m = st.number_input("Grasas (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: res_c = {"n":n_m, "k":k_m, "p":p_m, "c":c_m, "g":g_m}

    if res_c:
        st.session_state.k_t += res_c['k']
        st.session_state.p_t += res_c['p']
        st.session_state.c_t += res_c['c']
        st.session_state.g_t += res_c['g']
        try:
            supabase.table('registros_comida').insert({
                "usuario": u_nom, "comida": res_c['n'], "kcal": res_c['k'],
                "proteina": res_c['p'], "carbos": res_c['c'], "grasas": res_c['g']
            }).execute()
        except: pass
        
        st.success(f"✅ ¡{res_c['n']} registrado!")
        st.markdown(f"""
        <div style="background:#1a1a1a; border:2px solid #59402a; border-radius:10px; padding:15px; color:white; font-family:monospace; text-align:center;">
            <div style="font-weight:bold; color:#00FF41; margin-bottom:10px;">{res_c['n'].upper()}</div>
            <div style="display:flex; justify-content:space-around;">
                <div>🔥<br>{res_c['k']}<br>Kcal</div>
                <div>🍗<br>{res_c['p']}g<br>Prot</div>
                <div>🍚<br>{res_c['c']}g<br>Carb</div>
                <div>🥑<br>{res_c['g']}g<br>Gras</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.rerun()

st.divider()
try:
    hist = supabase.table('registros_comida').select('*').order('created_at', desc=True).limit(5).execute()
    for r in hist.data:
        st.write(f"🍴 **{r['comida']}**: {r['kcal']}kcal | P:{r['proteina']}g C:{r['carbos']}g G:{r['grasas']}g")
except: pass
