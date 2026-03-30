import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client
import re # ¡Importante para limpiar la respuesta de la IA!

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis: Maestro Xavier", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error(f"🚨 Error de Secrets o Conexión: {e}")
    st.stop()

# --- 2. PERFIL Y SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Protocolo de Inicio Jarvis")
    with st.form("registro_inicial"):
        c1, c2 = st.columns(2)
        nom = st.text_input("Usuario:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = c1.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ACCEDER"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_obj = obj
            st.rerun()
    st.stop()

# --- 3. LÓGICA DE METAS Y PASOS ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
if 'h2o' not in st.session_state: st.session_state.h2o = 0.0
if 'steps' not in st.session_state: st.session_state.steps = 0

obj_act = st.session_state.get('u_obj', "Hipertrofia")
meta_k = 3200.0 if obj_act == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 # 138.6g para Xavier
meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if obj_act == "Fútbol" else 0.6)
kcal_pasos = (st.session_state.steps / 1000) * 38

# --- 4. DASHBOARD ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.subheader("👣 Pasos")
    st.session_state.steps = st.number_input("Hoy:", 0, 50000, st.session_state.steps, step=500)
    st.write(f"🔥 Quemado: **{kcal_pasos:.0f} kcal**")
    st.subheader("💧 Agua")
    prog_h = min(st.session_state.h2o / meta_agua, 1.0)
    st.progress(prog_h)
    if st.button("➕ 500ml"): st.session_state.h2o += 0.5; st.rerun()
    if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

st.title(f"📊 Dashboard: {st.session_state.u_nom}")
p_act, k_act = 0.0, 0.0
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.date
        hoy_df = df[df['f'] == hoy.date()]
        k_act, p_act = hoy_df['kcal'].sum(), hoy_df['proteina'].sum()
except: pass

st.subheader(f"Objetivo Actual: {obj_act}")
cm1, cm2 = st.columns(2)
with cm1:
    st.write(f"🔥 Calorías Diarias: **{k_act:.0f}/{meta_k:.0f} kcal**")
    st.progress(min(k_act / meta_k, 1.0))
with cm2:
    st.write(f"🍗 Proteína ($2.2 \times \text{{peso}}$): **{p_act:.1f}/{meta_p:.0f}g**")
    st.progress(min(p_act / meta_p, 1.0))

m1, m2 = st.columns(2)
m1.metric("Falta Proteína", f"{max(meta_p - p_act, 0.0):.1f}g", help="Crucial para hipertrofia de pierna/glúteo")
m2.metric("Pasos Quemados", f"{kcal_pasos:.0f} kcal")

st.divider()
col1, col2 = st.columns([2,1])
with col1:
    st.subheader("📸 Registro con Foto (Análisis IA)")
    foto = st.file_uploader("Sube tu plato", type=["jpg", "png", "jpeg"])
    if foto and st.button("🔍 ANALIZAR COMIDA"):
        with st.spinner("🤖 Jarvis procesando..."):
            try:
                img_data = base64.b64encode(foto.read()).decode()
                
                # --- PROMPT BLINDADO v68.8 ---
                # Este mensaje es agresivo y obliga a la IA a responder SOLO los números.
                prompt = f"Analiza la comida de la imagen para el usuario Xavier (63kg). Responde EXCLUSIVAMENTE con este formato exacto: Nombre|Calorias|Proteina. Nada mas. Ejemplo: Batido Proteina|350|25"
                
                payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_data}}]}]}
                r = requests.post(URL_AI, json=payload).json()
                
                if 'candidates' in r and r['candidates']:
                    res_raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    st.write(f"🤖 Respuesta IA: `{res_raw}`") # Para verificar lo que responde
                    
                    data = res_raw.split('|')
                    if len(data) >= 3:
                        # --- LIMPIEZA TÉCNICA REGLAMENTARIA (re.sub) ---
                        # Eliminamos cualquier letra o símbolo que la IA haya inventado (kcal, g, etc.)
                        k_v = float(re.sub(r'[^\d.]', '', data[1]))
                        p_v = float(re.sub(r'[^\d.]', '', data[2]))
                        
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":data[0], "kcal":k_v, "proteina":p_v, "semana":inicio_sem}).execute()
                        st.success(f"✅ Registrado: {data[0]} ({k_v} kcal, {p_v}g P)")
                        st.rerun()
                    else: st.error("⚠️ La IA no usó el formato Nombre|Kcal|Prot. Intenta de nuevo.")
                else: st.error("⚠️ Google Gemini no respondió. Revisa tu API Key o la imagen.")
            except Exception as e: st.error(f"Error técnico en el análisis: {e}")

with col2:
    st.subheader("✍️ Registro Manual")
    with st.form("manual"):
        c_m = st.text_input("Comida:", placeholder="Ej: Pollo con Arroz")
        k_m = st.number_input("Kcal:", 0.0, 3000.0, 500.0)
        p_m = st.number_input("Prot (g):", 0.0, 200.0, 30.0)
        if st.form_submit_button("💾 GUARDAR"):
            supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":c_m, "kcal":k_m, "proteina":p_m, "semana":inicio_sem}).execute()
            st.success(f"✅ Guardado manualmente")
            st.rerun()

# --- 5. GRÁFICOS SEMANALES ---
if k_act > 0:
    st.plotly_chart(px.pie(values=[p_act*4, k_act-(p_act*4)], names=['Proteína', 'Otros'], hole=0.4, title="Macros de Hoy (Kcal)"))
