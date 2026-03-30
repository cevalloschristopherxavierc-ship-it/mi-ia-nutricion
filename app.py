import streamlit as st
import requests, base64, re, pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis: Xavier", layout="wide", page_icon="🦾")
try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("🚨 Revisa los Secrets en Streamlit.")
    st.stop()

# --- 2. SESIÓN ---
if 'u_nom' not in st.session_state:
    with st.form("reg"):
        st.title("🦾 Activación Jarvis")
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ENTRAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. METAS ---
hoy = datetime.now()
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
m_k = 3200 if st.session_state.u_obj == "Fútbol" else 2750
m_p = st.session_state.u_pes * 2.2 # Meta de 139g para Xavier
m_c = m_k * 0.5 / 4 # Meta estimada de Carbohidratos

# --- 4. DATA ---
k_act, p_act, c_act = 0.0, 0.0, 0.0
df_h, df_a = pd.DataFrame(), pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', ini_s).execute()
    if res.data:
        df_a = pd.DataFrame(res.data)
        df_a['f'] = pd.to_datetime(df_a['created_at']).dt.date
        df_h = df_a[(df_a['usuario'] == st.session_state.u_nom) & (df_a['f'] == hoy.date())]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
        # Si no tienes columna 'carbs' en Supabase todavía, lo estimamos para el gráfico:
        c_act = (k_act - (p_act * 4)) / 4 if k_act > 0 else 0
except: pass

# --- 5. UI DASHBOARD ---
st.title(f"📊 Panel {st.session_state.u_nom}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔥 Kcal", f"{k_act:.0f}/{m_k}")
col2.metric("🍗 Prot", f"{p_act:.1f}/{m_p:.0f}g")
col3.metric("🍞 Carb", f"{c_act:.0f}/{m_c:.0f}g")
col4.metric("🏃 Quemado", f"0 kcal") # Próximamente integración de pasos

t1, t2, t3, t4 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 DIARIO", "🕵️ CREADOR"])

with t1:
    ca, cb = st.columns(2)
    with ca:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    # Prompt optimizado para evitar "Error IA"
                    prompt = "Responde solo en este formato: Nombre|Calorias|Proteina. Ejemplo: Pollo con arroz|500|30"
                    pay = {"contents": [{"parts": [{"text": prompt},{"inline_data": {"mime_type": "image/jpeg", "data": img}}]}]}
                    r = requests.post(URL_AI, json=pay, timeout=15).json()
                    res_txt = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    pts = res_txt.split('|')
                    if len(pts) >= 3:
                        kv = float(re.findall(r"\d+", pts[1])[0])
                        pv = float(re.findall(r"\d+", pts[2])[0])
                        supabase.table('registros_comida').insert({
                            "usuario": st.session_state.u_nom, "comida": pts[0], 
                            "kcal": kv, "proteina": pv, "semana": ini_s
                        }).execute()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error IA: Asegúrate que la foto sea clara.")

    with cb:
        st.subheader("✍️ Manual")
        with st.form("m_en"):
            cm = st.text_input("Comida")
            pm = st.number_input("Prot (g)", 0.0)
            km = st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({
                    "usuario": st.session_state.u_nom, "comida": cm, 
                    "kcal": km, "proteina": pm, "semana": ini_s
                }).execute()
                st.rerun()

with t2:
    if k_act > 0:
        st.plotly_chart(px.pie(values=[p_act*4, c_act*4, (k_act*0.2)], names=['Prot', 'Carb', 'Grasas'], hole=0.5, template="plotly_dark"))
    else:
        st.info("Registra comida para ver el gráfico.")

with t3:
    st.subheader("📝 Registros de Hoy")
    if not df_h.empty:
        st.dataframe(df_h[['comida', 'kcal', 'proteina']], use_container_width=True)

with t4:
    cod = st.sidebar.text_input("🔐 Código Creador:", type="password")
    if cod == "xavier2210":
        st.subheader("🕵️ Panel Creador Activo")
        if not df_a.empty:
            sel = st.selectbox("Ver usuario:", df_a['usuario'].unique())
            st.dataframe(df_a[df_a['usuario'] == sel], use_container_width=True)
    else:
        st.warning("Introduce el código en la barra lateral para acceder.")
