import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px  # <-- ESTA LÍNEA ES LA QUE FALTABA
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIG & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Fit Xavier", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error(f"⚠️ Revisa los Secrets: {e}")
    st.stop()

# --- 2. SESSION STATE ---
for k in ['k_t', 'p_t', 'c_t', 'g_t']:
    if k not in st.session_state: st.session_state[k] = 0.0

# --- 3. SIDEBAR: SELECTOR & HIDRATACIÓN ---
with st.sidebar:
    st.title("🦾 NÚCLEO DE JARVIS")
    u_nom = "Xavier"
    u_pes = 63.0
    
    modo = st.radio("¿Qué toca hoy?", ["Gym (Pierna/Glúteo)", "Fútbol (Partido 2h)"])
    
    if modo == "Fútbol (Partido 2h)":
        meta_k = 3000.0
        st.warning("⚽ Modo Fútbol: Meta 3000 kcal.")
    else:
        meta_k = 2500.0
    
    st.divider()
    
    # Calculadora de Agua (35ml x kg)
    agua_total = ((u_pes * 35) / 1000) + (1.0 if modo == "Fútbol (Partido 2h)" else 0.5)
    st.subheader("💧 Hidratación")
    st.info(f"Objetivo: **{agua_total:.2f} Litros**")
    if modo == "Fútbol (Partido 2h)":
        st.error("🔥 ALERTA MANABÍ: Toma agua constante en el partido.")

    st.divider()
    prog = min(st.session_state.k_t / meta_k, 1.0)
    st.write(f"🔥 Progreso: {int(prog*100)}%")
    st.progress(prog)

# --- 4. DASHBOARD & ALERTAS ---
st.title(f"📈 Dashboard: {u_nom}")

# Alarma de Proteína (Después de las 4 PM)
hora_actual = datetime.now().hour
if hora_actual >= 16 and st.session_state.p_t < 60:
    st.warning(f"🚨 ¡XAVIER! Llevas poca proteína ({st.session_state.p_t:.1f}g). ¡Dale al huevo o batido!")

t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    
    # Gráfica corregida
    df = pd.DataFrame({'M':['Prot','Carb','Gras'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    fig = px.pie(df, values='G', names='M', hole=0.5, template="plotly_dark", color_discrete_sequence=['#00FF41','#FFC107','#2196F3'])
    st.plotly_chart(fig, use_container_width=True)

with t2:
    col_f, col_m = st.columns(2)
    res_c = None
    with col_f:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    prompt = f"Responde SOLO: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    d = raw.replace(' ','').replace('g','').replace('kcal','').replace('*','').split('|')
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
