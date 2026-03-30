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

# --- 3. LÓGICA DE METAS Y HORARIO ---
hoy = datetime.now()
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_nombre = dias_semana[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

rutina = {
    "Lunes": "🍗 Piernas / Glúteos (Enfoque Hipertrofia)",
    "Martes": "👕 Pecho / Tríceps / Hombros",
    "Miércoles": "🔙 Espalda / Bíceps",
    "Jueves": "🍗 Piernas / Glúteos (Repetición)",
    "Viernes": "⚽ Fútbol / Cardio Intenso",
    "Sábado": "👕 Pecho / Tríceps / Hombros (o Repetición)",
    "Domingo": "🛌 Descanso Total (Rest Day)"
}

if 'h2o' not in st.session_state: st.session_state.h2o = 0.0
if 'steps' not in st.session_state: st.session_state.steps = 0

obj_act = st.session_state.get('u_obj', "Hipertrofia")
meta_k = 3200.0 if obj_act == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4
meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if obj_act == "Fútbol" else 0.6)
kcal_pasos = (st.session_state.steps / 1000) * 38

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 Perfil: {st.session_state.u_nom}")
    st.info(f"📅 Hoy es **{dia_nombre}**\n\n🎯 Tarea: {rutina.get(dia_nombre)}")
    st.divider()
    st.subheader("👣 Actividad")
    st.session_state.steps = st.number_input("Pasos:", 0, 50000, st.session_state.steps, step=500)
    st.write(f"🔥 Quemado: **{kcal_pasos:.0f} kcal**")
    
    st.divider()
    st.subheader("💧 Hidratación")
    prog_h = min(st.session_state.h2o / meta_agua, 1.0)
    st.progress(prog_h)
    if st.button("➕ 500ml"): 
        st.session_state.h2o += 0.5
        st.rerun()

    if st.session_state.u_nom.lower() == "xavier":
        st.divider()
        st.subheader("🕵️ Panel Maestro")
        target = st.text_input("Vigilar Discípulo:", placeholder="Nombre")
        btn_vigilar = st.button("👁️ Rastrear")
    else: btn_vigilar = False

# --- 5. DASHBOARD PRINCIPAL ---
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

st.subheader(f"Objetivo: {obj_act}")
cm1, cm2, cm3, cm4 = st.columns(4)
with cm1: st.metric("Kcal", f"{k_act:.0f}/{meta_k:.0f}")
with cm2: st.metric("Prot", f"{p_act:.1f}g", f"/{meta_p:.0f}g")
with cm3: st.metric("Gasto Pasos", f"{kcal_pasos:.0f}")
with cm4: st.metric("Balance Neto", f"{(k_act - kcal_pasos):.0f}")

t1, t2, t3 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 HORARIO"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📸 Foto IA (Análisis)")
        foto = st.file_uploader("Sube tu plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR COMIDA"):
            with st.spinner("🤖 Jarvis procesando..."):
                try:
                    img_b64 = base64.b64encode(foto.read()).decode()
                    # PROMPT TÉCNICO REFORZADO
                    prompt = "Analiza esta comida. Responde UNICAMENTE en este formato exacto: Nombre|Calorias|Proteina. Ejemplo: Arroz con pollo|500|30"
                    payload = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=payload).json()
                    
                    if 'candidates' in r and r['candidates']:
                        texto = r['candidates'][0]['content']['parts'][0]['text'].strip()
                        partes = texto.split('|')
                        if len(partes) >= 3:
                            nom_c = partes[0].strip()
                            # Captura de números con mayor precisión
                            k_v = float(re.findall(r"\d+\.?\d*", partes[1])[0])
                            p_v = float(re.findall(r"\d+\.?\d*", partes[2])[0])
                            
                            supabase.table('registros_comida').insert({
                                "usuario": st.session_state.u_nom, "comida": nom_c, 
                                "kcal": k_v, "proteina": p_v, "semana": inicio_sem
                            }).execute()
                            st.success(f"✅ Registrado: {nom_c}")
                            st.rerun()
                    else: st.error("⚠️ La IA no devolvió datos. Intenta subir la foto otra vez.")
                except Exception as e: st.error(f"Error de análisis: {e}")

    with col_b:
        st.subheader("✍️ Registro Manual")
        with st.form("man"):
            c_m = st.text_input("Comida")
            p_m = st.number_input("Proteína (g)", 0.0)
            k_m = st.number_input("Calorías", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":c_m, "kcal":k_m, "proteina":p_m, "semana":inicio_sem}).execute()
                st.rerun()

with t2:
    if k_act > 0:
        fig = px.pie(values=[p_act*4, (k_act*0.5), (k_act*0.25)], names=['Prot', 'Carb', 'Gras'], hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Registra comida para ver el análisis de macros.")

with t3:
    st.subheader("🗓️ Tu Plan Maestro Semanal")
    df_rutina = pd.DataFrame(list(rutina.items()), columns=["Día", "Entrenamiento / Actividad"])
    st.table(df_rutina)
    st.info("💡 Recuerda: Los viernes de fútbol el gasto calórico es mayor. ¡Asegúrate de comer lo suficiente!")

# --- 6. VIGILANCIA ---
if btn_vigilar and target:
    st.divider()
    st.header(f"🕵️ Reporte: {target}")
    try:
        res_t = supabase.table('registros_comida').select('*').eq('usuario', target.strip()).eq('semana', inicio_sem).execute()
        if res_t.data:
            dt = pd.DataFrame(res_t.data)
            st.metric(f"Proteína de {target}", f"{dt['proteina'].sum():.1f}g")
            st.table(dt[['comida', 'proteina', 'kcal']])
    except: st.error("Error al buscar discípulo.")
