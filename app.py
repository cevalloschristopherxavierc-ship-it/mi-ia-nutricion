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
    # Usamos modelo 1.5-flash para mejor detección de fotos
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("🚨 Error de Secrets. Verifica Supabase y Gemini.")
    st.stop()

# --- 2. PERFIL Y SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    with st.form("registro"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = c1.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. LÓGICA NUTRICIONAL Y TIEMPO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
if 'h2o' not in st.session_state: st.session_state.h2o = 0.0
if 'steps' not in st.session_state: st.session_state.steps = 0

# Blindaje de metas
obj_act = st.session_state.get('u_obj', "Hipertrofia")
meta_k = 3200.0 if obj_act == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if obj_act == "Fútbol" else 0.6)

# --- 4. SIDEBAR (METAS, AGUA Y CREADOR) ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.divider()
    
    st.subheader("💧 Hidratación")
    prog_agua = min(st.session_state.h2o / meta_agua, 1.0)
    st.progress(prog_agua)
    st.write(f"Llevas: **{st.session_state.h2o:.1f}L** / {meta_agua:.1f}L")
    if st.button("➕ Beber 500ml"): 
        st.session_state.h2o += 0.5
        st.rerun()
    
    st.divider()
    st.subheader("📊 Tus Metas")
    st.info(f"🔥 Kcal: **{meta_k:.0f}**")
    st.info(f"🍗 Prot: **{meta_p:.0f}g**")
    
    st.divider()
    st.subheader("🕵️ Panel Maestro")
    target = st.text_input("Vigilar Discípulo:", placeholder="Nombre")
    btn_vigilar = st.button("👁️ Rastrear")
    
    if st.button("🔄 Reiniciar"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD PRINCIPAL ---
st.title(f"📊 Dashboard: {st.session_state.u_nom}")

# Carga de datos desde Supabase
p_act, k_act = 0.0, 0.0
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.date
        hoy_df = df[df['f'] == hoy.date()]
        k_act, p_act = hoy_df['kcal'].sum(), hoy_df['proteina'].sum()
except: pass

# Mensaje Motivador Bonus
if p_act >= meta_p and st.session_state.steps >= 8000:
    st.balloons()
    st.success("🔥 ¡Es hora de ponerte mamado y fuerte! 🔥")

# Métricas Visuales
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kcal", f"{k_act:.0f}", f"/{meta_k:.0f}")
m2.metric("Proteína", f"{p_act:.1f}g", f"/{meta_p:.0f}g")
m3.metric("Agua", f"{st.session_state.h2o:.1f}L", f"/{meta_agua:.1f}L")
m4.metric("Pasos", f"{st.session_state.steps}", "/8000")

t1, t2 = st.tabs(["📈 ANÁLISIS", "🍽️ REGISTRO"])

with t1:
    if k_act > 0:
        fig = px.pie(values=[p_act*4, abs(k_act-(p_act*4)-400), 400], 
                     names=['Prot', 'Carb', 'Gras'], 
                     hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra tu primera comida para ver el análisis.")

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
                        nombre_c = data[0].strip()
                        # Limpieza de números (extrae solo dígitos)
                        k_val = float(''.join(re.findall(r'\d+', data[1])))
                        p_val = float(''.join(re.findall(r'\d+', data[2])))
                        
                        supabase.table('registros_comida').insert({
                            "usuario": st.session_state.u_nom, "comida": nombre_c, 
                            "kcal": k_val, "proteina": p_val, "semana": inicio_sem
                        }).execute()
                        st.success(f"✅ Guardado: {nombre_c}")
                        st.rerun()
                except: st.error("Error IA. Revisa iluminación o formato.")
    
    with col_b:
