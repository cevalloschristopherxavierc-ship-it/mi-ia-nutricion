import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Creator Mode", layout="wide", page_icon="👑")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PERFIL ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Activación de Núcleo Jarvis")
    with st.form("perfil_inicial"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Tu nombre?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 INICIAR SISTEMA"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. TIEMPO Y ESTADO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
if 'agua_hoy' not in st.session_state: st.session_state.agua_hoy = 0.0
if 'pasos_hoy' not in st.session_state: st.session_state.pasos_hoy = 0

# --- 4. SIDEBAR (MODO CREADOR) ---
with st.sidebar:
    st.title(f"👑 Creador: {st.session_state.u_nom}")
    modo = st.radio("Tu actividad:", ["Gym", "Fútbol"])
    
    st.divider()
    st.subheader("👁️ Supervisar Discípulos")
    discípulo = st.text_input("Nombre del discípulo:")
    ver_datos = st.button("🔍 Ver Progreso")
    
    st.divider()
    if st.button("➕ Beber 500ml"):
        st.session_state.agua_hoy += 0.5
        st.rerun()
    st.write(f"💧 Agua: {st.session_state.agua_hoy:.1f}L")
    st.session_state.pasos_hoy = st.number_input("Tus pasos:", 0, 40000, st.session_state.pasos_hoy)

# --- 5. LÓGICA DE SUPERVISIÓN (MODO CREADOR) ---
if ver_datos and discípulo:
    st.header(f"🕵️ Análisis de Discípulo: {discípulo}")
    try:
        res_d = supabase.table('registros_comida').select('*').eq('usuario', discípulo.strip()).eq('semana', inicio_sem).execute()
        if res_d.data:
            df_d = pd.DataFrame(res_d.data)
            df_d['f'] = pd.to_datetime(df_d['created_at']).dt.date
            hoy_d = df_d[df_d['f'] == hoy.date()]
            
            k_d, p_d = hoy_d['kcal'].sum(), hoy_d['proteina'].sum()
            
            m1, m2 = st.columns(2)
            m1.metric(f"Calorías de {discípulo}", f"{k_d:.0f} kcal")
            m2.metric(f"Proteína de {discípulo}", f"{p_d:.1f}g")
            
            st.subheader("Últimas comidas del discípulo:")
            st.table(hoy_d[['comida', 'kcal', 'proteina']])
            
            if p_d < 100: st.warning(f"⚠️ {discípulo} está bajo en proteína. ¡Dile que deje de flojear!")
            else: st.success(f"✅ {discípulo} está cumpliendo como un guerrero.")
        else:
            st.info(f"El discípulo '{discípulo}' no tiene registros hoy.")
    except: st.error("Error al buscar al discípulo.")
    st.divider()

# --- 6. TU DASHBOARD PERSONAL ---
st.title(f"📊 Tu Progreso: {st.session_state.u_nom}")
p_act = 0.0 
try:
    res = supabase.table('registros_comida').select('proteina').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data: p_act = sum(float(r['proteina']) for r in res.data)
except: pass

# Meta personal simplificada
meta_p = st.session_state.u_pes * 2.2
if p_act >= meta_p and st.session_state.pasos_hoy >= 8000:
    st.balloons()
    st.info("🔥 🔥 **'¡Es hora de ponerte mamado y fuerte!'** 🔥 🔥")

t1, t2 = st.tabs(["📈 TUS STATS", "🍽️ REGISTRAR TU COMIDA"])

with t1:
    res_db = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    df = pd.DataFrame(res_db.data) if res_db.data else pd.DataFrame()
    if not df.empty:
        df['f_dt'] = pd.to_datetime(df['created_at']).dt.date
        h_d = df[df['f_dt'] == hoy.date()]
        st.metric("Tu Prot Hoy", f"{h_d['proteina'].sum():.1f}g", f"Meta: {meta_p:.0f}g")
        st.plotly_chart(px.bar(h_d, x='comida', y='proteina', template="plotly_dark"), use_container_width=True)

with t2:
    foto = st.file_uploader("Foto de tu plato", type=["jpg","png"])
    if foto and st.button("🔍 ANALIZAR MI PLATO"):
        with st.spinner("🤖 Jarvis analizando..."):
            try:
                img = base64.b64encode(foto.read()).decode()
                pld = {"contents":[{"parts":[{"text":"Nombre|Kcal|Prot|Carb|Gras"},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                r = requests.post(URL_AI, json=pld).json()
                d = r['candidates'][0]['content']['parts'][0]['text'].strip().split('|')
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":d[0], "kcal":float(d[1]), "proteina":float(d[2]), "semana":inicio_sem}).execute()
                st.success("Guardado en tu perfil.")
                st.rerun()
            except: st.error("Error en IA.")

# --- 7. REGISTRO MANUAL RÁPIDO ---
with st.expander("✍️ Registro Manual"):
    with st.form("manual"):
        com = st.text_input("Comida")
        prot = st.number_input("Proteína (g)", 0.0)
        kcal = st.number_input("Kcal", 0.0)
        if st.form_submit_button("💾 GUARDAR"):
            supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":com, "kcal":kcal, "proteina":prot, "semana":inicio_sem}).execute()
            st.rerun()
