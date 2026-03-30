import streamlit as st
import requests
import base64
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIG & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Fit Xavier", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. SESSION STATE (MEMORIA) ---
for k in ['k_t', 'p_t', 'c_t', 'g_t']:
    if k not in st.session_state: st.session_state[k] = 0.0

# --- 3. SIDEBAR: SELECTOR DE ENTRENAMIENTO & PERFIL ---
with st.sidebar:
    st.title("🦾 NÚCLEO DE JARVIS")
    u_nom = "Xavier"
    u_pes = 63.0
    
    # --- IDEA 3: SELECTOR DE ENTRENAMIENTO ---
    modo = st.radio("¿Qué toca hoy?", ["Gym (Hipertrofia)", "Fútbol (Partido 2h)"])
    
    if modo == "Fútbol (Partido 2h)":
        meta_k = 3000.0 # Subimos 500kcal por el desgaste en Portoviejo
        st.warning("⚽ Modo Fútbol: Meta subida a 3000 kcal.")
    else:
        meta_k = 2500.0
    
    st.divider()
    
    # --- IDEA 1: CALCULADORA DE HIDRATACIÓN ---
    # Fórmula: 35ml por kg + 1 litro extra por deporte intenso
    agua_base = (u_pes * 35) / 1000 
    agua_total = agua_base + 1.0 if modo == "Fútbol (Partido 2h)" else agua_base + 0.5
    
    st.subheader("💧 Hidratación")
    st.info(f"Debes tomar: **{agua_total:.2f} Litros**")
    if modo == "Fútbol (Partido 2h)":
        st.error("🔥 ALERTA MANABÍ: El sol está fuerte. Toma 1 vaso cada 20 min en el partido.")

    st.divider()
    prog = min(st.session_state.k_t / meta_k, 1.0)
    st.write(f"🔥 Progreso: {int(prog*100)}%")
    st.progress(prog)

# --- 4. DASHBOARD & ALERTAS ---
st.title(f"📈 Dashboard Nutricional")

# --- IDEA 2: ALARMA DE PROTEÍNA INTELIGENTE ---
hora_actual = datetime.now().hour
if hora_actual >= 16 and st.session_state.p_t < 60:
    st.warning(f"🚨 ¡XAVIER! Son más de las 4 PM y solo llevas {st.session_state.p_t:.1f}g de proteína. ¡Cómete un huevo o un batido ahora!")

t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    
    df = pd.DataFrame({'M':['Prot','Carb','Gras'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    st.plotly_chart(px.pie(df, values='G', names='M', hole=0.5, template="plotly_dark"), use_container_width=True)

with t2:
    col_f, col_m = st.columns(2)
    res_c = None
    with col_f:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    prompt = f"Responde SOLO: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    d = raw.replace(' ','').replace('g','').replace('kcal','').split('|')
                    res_c = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
                except: st.error("❌ Error IA")

    with col_m:
        st.subheader("✍️ Manual")
        with st.form("f_m"):
            n_m = st.text_input("Plato")
            k_m = st.number_input("Kcal", 0.0)
            p_m = st.number_input("Prot", 0.0)
            c_m = st.number_input("Carb", 0.0)
            g_m = st.number_input("Gras", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: res_c = {"n":n_m, "k":k_m, "p":p_m, "c":c_m, "g":g_m}

    if res_c:
        st.session_state.k_t += res_c['k']
        st.session_state.p_t += res_c['p']
        st.session_state.c_t += res_c['c']
        st.session_state.g_t += res_c['g']
        try:
            supabase.table('registros_comida').insert({"usuario": u_nom, "comida": res_c['n'], "kcal": res_c['k'], "proteina": res_c['p'], "carbos": res_c['c'], "grasas": res_c['g']}).execute()
            st.success("✅ Guardado")
            st.rerun()
        except: st.error("❌ Error al guardar")

# --- HISTORIAL ---
st.divider()
try:
    hist = supabase.table('registros_comida').select('*').order('created_at', desc=True).limit(5).execute()
    for r in hist.data:
        st.write(f"🍴 **{r['comida']}**: {r['kcal']}kcal | P:{r['proteina']}g C:{r['carbos']}g G:{r['grasas']}g")
except: pass
