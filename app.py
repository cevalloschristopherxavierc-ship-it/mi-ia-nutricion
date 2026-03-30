import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis: Maestro Xavier", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("🚨 Error de Secrets. Verifica Supabase y Gemini.")
    st.stop()

# --- 2. PERFIL Y SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    with st.form("registro_inicial"):
        c1, c2 = st.columns(2)
        nom = st.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. TIEMPO Y METAS ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = dias[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

plan_entreno = {
    "Lunes": "🍗 Piernas / Glúteos (Fuerza)", "Martes": "👕 Pecho / Tríceps / Hombros",
    "Miércoles": "🔙 Espalda / Bíceps", "Jueves": "🍗 Piernas / Glúteos (Hipertrofia)",
    "Viernes": "⚽ Fútbol / Cardio Explosivo", "Sábado": "👕 Torso Superior", "Domingo": "🛌 Descanso"
}

meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. DATA REAL ---
p_act, k_act, c_act, g_act = 0.0, 0.0, 0.0, 0.0
df_hoy = pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[df_all['fecha'] == hoy.date()]
        if not df_hoy.empty:
            k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
            # Cálculo de macros basado en lo ingerido
            c_act = (k_act * 0.5) / 4
            g_act = (k_act * 0.25) / 9
except: pass

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard Nutricional: {st.session_state.u_nom}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🔥 Kcal", f"{k_act:.0f}", f"/{meta_k:.0f}")
m2.metric("🍗 Prot", f"{p_act:.1f}g", f"/{meta_p:.0f}g")
m3.metric("🍚 Carb (Est.)", f"{c_act:.1f}g")
m4.metric("🥑 Gras (Est.)", f"{g_act:.1f}g")

t1, t2, t3 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 DIARIO Y HORARIO"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube tu plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis procesando..."):
                try:
                    img_b64 = base64.b64encode(foto.read()).decode()
                    payload = {"contents":[{"parts":[{"text":"Nombre|Kcal|Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=payload).json()
                    txt_ia = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    partes = txt_ia.split('|')
                    if len(partes) >= 3:
                        kv = float(re.findall(r"\d+", partes[1])[0])
                        pv = float(re.findall(r"\d+", partes[2])[0])
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":partes[0].strip(), "kcal":kv, "proteina":pv, "semana":inicio_sem}).execute()
                        st.rerun()
                except: st.error("Error al procesar foto.")
    with col_b:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_entry"):
            cm = st.text_input("Comida")
            pm = st.number_input("Proteína (g)", 0.0)
            km = st.number_input("Calorías (kcal)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":cm, "kcal":km, "proteina":pm, "semana":inicio_sem}).execute()
                st.rerun()

with t2:
    st.subheader("🥧 Distribución de Macronutrientes")
    if k_act > 0:
        # Gráfico circular profesional
        fig = px.pie(
            values=[p_act*4, c_act*4, g_act*9], 
            names=['Proteína', 'Carbohidratos', 'Grasas'], 
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos para analizar
