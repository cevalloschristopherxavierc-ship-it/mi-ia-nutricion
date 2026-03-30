import streamlit as st
import requests, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from supabase import create_client, Client

# --- 1. IDENTIDAD XAVIER (63KG - PORTOVIEJO) ---
st.set_page_config(page_title="Jarvis OS | Xavier", layout="wide", page_icon="🦾")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- 2. SESIÓN Y METAS ---
if 'u_nom' not in st.session_state:
    st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = "Xavier", 63.0, "Fútbol"
    st.session_state.h2o = 0.0

meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2800.0
meta_p = 138.6 # Tu meta crítica para hipertrofia

# --- 3. SIDEBAR (HIDRATACIÓN Y PASOS) ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación (3.5L)")
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Nivel: **{st.session_state.h2o:.1f}L**")
    if st.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    st.divider()
    pasos = st.number_input("👣 Pasos hoy:", 0, 50000, 0, 500)
    st.metric("Gasto Estimado", f"{(pasos/1000)*40:.0f} Kcal")
    if st.text_input("🔐 Creador:", type="password") == "xavier2210":
        st.session_state.creador = True

# --- 4. DATA SYNC ---
k_act, p_act = 0.0, 0.0
try:
    hoy = datetime.now().strftime('%Y-%m-%d')
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        df_h = df[df['f'] == hoy]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
except: pass

# --- 5. DASHBOARD ---
st.header("📊 Centro de Mando Jarvis")
m1, m2 = st.columns(2)
m1.metric("🔥 Kcal", f"{k_act:.0f}/{meta_k:.0f}")
m2.metric("🍗 Prot", f"{p_act:.1f}/{meta_p:.1f}g")

tabs = st.tabs(["🍽️ REGISTRO INTELIGENTE", "💪 ANÁLISIS", "🕵️ CREADOR"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🤖 Analizador de Texto (Sin Error 404)")
        txt_input = st.text_input("Escribe tu comida (ej: '3 huevos cocidos'):")
        if st.button("🔍 CALCULAR") and txt_input:
            with st.spinner("🤖 Jarvis calculando macros..."):
                try:
                    key = st.secrets["GEMINI_API_KEY"]
                    # USAMOS EL MODELO DE TEXTO QUE NO DA ERROR 404
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
                    payload = {"contents":[{"parts":[{"text": f"Calcula Kcal y Proteína para: {txt_input}. Responde solo: Nombre, Kcal, Prot"}]}]}
                    r = requests.post(url, json=payload, timeout=20)
                    if r.status_code == 200:
                        txt = r.json()['candidates'][0]['content']['parts'][0]['text']
                        nums = re.findall(r"\d+", txt)
                        if len(nums) >= 2:
                            supabase.table('registros_comida').insert({"usuario":"Xavier","comida":txt_input,"kcal":float(nums[0]),"proteina":float(nums[1]),"semana":hoy}).execute()
                            st.success(f"✅ Registrado: {nums[0]} Kcal, {nums[1]}g Prot")
                            st.rerun()
                    else: st.error("Error de conexión. Usa el manual a la derecha.")
                except: st.error("Fallo de red.")

    with c2:
        st.subheader("✍️ Registro Manual (Seguro)")
        with st.form("f_man", clear_on_submit=True):
            n = st.text_input("Comida")
            k = st.number_input("Kcal", 0.0)
            p = st.number_input("Prot", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":"Xavier","comida":n,"kcal":k,"proteina":p,"semana":hoy}).execute()
                st.rerun()

with tabs[1]:
    if k_act > 0:
        fig = go.Figure(go.Scatterpolar(r=[p_act/meta_p, k_act/meta_k, 0.8, 0.7], theta=['Prot', 'Kcal', 'Carb', 'Grasa'], fill='toself', line_color='#4facfe'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
