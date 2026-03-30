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
    st.error("🚨 Error de conexión. Revisa tus Secrets.")
    st.stop()

# --- 2. PERFIL Y SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Activación de Jarvis")
    with st.form("registro"):
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 INICIAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. LÓGICA DE TIEMPO Y RUTINA ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = dias[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

rutina = {
    "Lunes": {"entreno": "🍗 Piernas/Glúteo (Fuerza)", "comida": "🍳 Huevos/Avena | 🍗 Pollo/Arroz | 🐟 Pescado"},
    "Martes": {"entreno": "👕 Pecho/Tríceps/Hombro", "comida": "🥤 Batido/Banano | 🥩 Carne/Pasta | 🍗 Pollo/Camote"},
    "Miércoles": {"entreno": "🔙 Espalda/Bíceps", "comida": "🍳 Claras/Pan | 🦃 Pavo/Arroz | 🐟 Atún/Ensalada"},
    "Jueves": {"entreno": "🍗 Piernas/Glúteo (Hipertrofia)", "comida": "🥣 Yogur/Nueces | 🍗 Pollo/Lentejas | 🍳 Huevos"},
    "Viernes": {"entreno": "⚽ Fútbol (Partido)", "comida": "🥣 Avena/Fruta | 🍝 Pasta/Pollo | 🥤 Batido Post"},
    "Sábado": {"entreno": "💪 Torso Superior", "comida": "🥞 Pancakes Avena | 🐟 Pescado/Papa | 🍗 Pollo"},
    "Domingo": {"entreno": "🛌 Descanso", "comida": "🥗 Ensaladas y Proteína base"}
}

# Metas Xavier (63kg)
meta_k = 3200 if st.session_state.u_obj == "Fútbol" else 2750
meta_p = st.session_state.u_pes * 2.2
if 'agua' not in st.session_state: st.session_state.agua = 0.0
if 'pasos' not in st.session_state: st.session_state.pasos = 0

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👤 {st.session_state.u_nom}")
    st.info(f"🏋️ **Hoy:** {rutina[dia_hoy]['entreno']}")
    st.subheader("💧 Agua")
    col_a1, col_a2 = st.columns(2)
    if col_a1.button("➕ 500ml"): st.session_state.agua += 0.5
    if col_a2.button("🧹 Limpiar"): st.session_state.agua = 0.0
    st.write(f"Total: **{st.session_state.agua}L**")
    
    st.subheader("👣 Pasos")
    st.session_state.pasos = st.number_input("Hoy:", 0, 50000, st.session_state.pasos, step=500)
    
    st.divider()
    # MODO CREADOR
    st.subheader("🔑 Modo Creador")
    cod = st.text_input("Código Maestro:", type="password")
    if cod == "Xavier123": # Cambia este código a tu gusto
        st.success("Acceso Creador Activo")
        st.session_state.creador = True
    else: st.session_state.creador = False

# --- 5. OBTENCIÓN DE DATOS ---
p_act, k_act = 0.0, 0.0
df_hoy = pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', inicio_sem).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[(df_all['usuario'] == st.session_state.u_nom) & (df_all['fecha'] == hoy.date())]
        k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
except: pass

# --- 6. DASHBOARD ---
st.title("📊 Jarvis Nutrición")
m1, m2, m3 = st.columns(3)
m1.metric("🔥 Calorías", f"{k_act:.0f}/{meta_k}")
m2.metric("🍗 Proteína", f"{p_act:.1f}g/{meta_p:.0f}g")
m3.metric("🏃 Quemado", f"{(st.session_state.pasos/1000)*38:.0f} kcal")

t1, t2, t3, t4 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 HORARIO/DIARIO", "🕵️ SUPERVISOR"])

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_b64 = base64.b64encode(foto.read()).decode()
                    payload = {"contents":[{"parts":[{"text":"Nombre|Kcal|Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=payload).json()
                    res_ia = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    pts = res_ia.split('|')
                    if len(pts) >= 3:
                        kv = float(re.findall(r"\d+", pts[1])[0])
                        pv = float(re.findall(r"\d+", pts[2])[0])
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":pts[0].strip(), "kcal":kv, "proteina":pv, "semana":inicio_sem}).execute()
                        st.rerun()
                except: st.error("Error IA")
    with c_b:
        st.subheader("✍️ Manual")
        with st.form("man"):
            cm = st.text_input("Comida")
            pm = st.number_input("Prot", 0.0)
            km = st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾"):
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":cm, "kcal":km, "proteina":pm, "semana":inicio_sem}).execute()
                st.rerun()

with t2:
    if k_act > 0:
        st.plotly_chart(px.pie(values=[p_act*4, k_act*0.5, k_act*0.25], names=['Prot', 'Carb', 'Gras'], hole=0.5, template="plotly_dark"))

with t3:
    st.subheader("📝 Tu Diario de Hoy")
    st.dataframe(df_hoy[['comida', 'kcal', 'proteina']], use_container_width=True)
    st.divider()
    st.subheader("🗓️ Horario Maestro")
    st.table(pd.DataFrame([{"Día": d, "Entreno": rutina[d]['entreno'], "Comida Sugerida": rutina[d]['comida']} for d in dias]))

with t4:
    if st.session_state.get('creador', False):
        st.subheader("🕵️ Panel de Supervisión (Creador)")
        usuarios = df_all['usuario'].unique()
        user_sel = st.selectbox("Ver datos de:", usuarios)
        df_user = df_all[df_all['usuario'] == user_sel]
        st.write(f"Registros totales de {user_sel}:")
        st.dataframe(df_user, use_container_width=True)
    else:
        st.warning("🔒 Acceso restringido. Ingresa el Código Maestro en el Sidebar.")
