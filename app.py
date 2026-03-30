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
        nom = c1.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = c1.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_obj = obj
            st.rerun()
    st.stop()

# --- 3. LÓGICA NUTRICIONAL Y PASOS ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

if 'h2o' not in st.session_state: st.session_state.h2o = 0.0
if 'steps' not in st.session_state: st.session_state.steps = 0

obj_act = st.session_state.get('u_obj', "Hipertrofia")
meta_k = 3200.0 if obj_act == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if obj_act == "Fútbol" else 0.6)

# Quema de calorías por pasos
kcal_pasos = (st.session_state.steps / 1000) * 38

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.divider()
    st.subheader("👣 Actividad")
    st.session_state.steps = st.number_input("Pasos hoy:", 0, 50000, st.session_state.steps, step=500)
    st.write(f"🔥 Quemado: **{kcal_pasos:.0f} kcal**")
    st.divider()
    st.subheader("💧 Hidratación")
    prog_agua = min(st.session_state.h2o / meta_agua, 1.0)
    st.progress(prog_agua)
    if st.button("➕ 500ml"): 
        st.session_state.h2o += 0.5
        st.rerun()
    if st.button("🔄 Reiniciar"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard: {st.session_state.u_nom}")
p_act, k_act = 0.0, 0.0
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.date
        hoy_df = df[df['f'] == hoy.date()]
        k_act, p_act = hoy_df['kcal'].sum(), hoy_df['proteina'].sum()
except:
    pass

m1, m2, m3, m4 = st.columns(4)
m1.metric("Kcal Comidas", f"{k_act:.0f}")
m2.metric("Proteína", f"{p_act:.1f}g", f"/{meta_p:.0f}g")
m3.metric("Kcal Pasos", f"{kcal_pasos:.0f}")
m4.metric("Balance Neto", f"{(k_act - kcal_pasos):.0f}")

t1, t2 = st.tabs(["📈 ANÁLISIS", "🍽️ REGISTRO"])

with t1:
    if k_act > 0:
        fig = px.pie(values=[p_act*4, abs(k_act-(p_act*4)-400), 400], names=['Prot', 'Carb', 'Gras'], hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin registros.")

with t2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","jpeg","png"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_data = base64.b64encode(foto.read()).decode()
                    prompt = "Responde SOLO: Nombre|Kcal|Proteina. Ejemplo: Pollo|500|30"
                    payload = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img_data}}]}]}
                    r = requests.post(URL_AI, json=payload).json()
                    res_raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    data = res_raw.split('|')
                    
                    if len(data) >= 3:
                        # CORRECCIÓN NAMEERROR: Definimos variables antes de usarlas
                        nombre_comida = data[0].strip()
                        k_v = float(''.join(re.findall(r'\d+', data[1])))
                        p_v = float(''.join(re.findall(r'\d+', data[2])))
                        
                        supabase.table('registros_comida').insert({
                            "usuario": st.session_state.u_nom, 
                            "comida": nombre_comida, 
                            "kcal": k_v, 
                            "proteina": p_v, 
                            "semana": inicio_sem
                        }).execute()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error IA: {str(e)[:30]}")

    with col_b:
        st.subheader("✍️ Manual")
        with st.form("manual_reg"):
            c_m = st.text_input("Comida")
            p_m = st.number_input("Prot (g)", 0.0)
            k_m = st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({
                    "usuario": st.session_state.u_nom, 
                    "comida": c_m, 
                    "kcal": k_m, 
                    "proteina": p_m, 
                    "semana": inicio_sem
                }).execute()
                st.rerun()
