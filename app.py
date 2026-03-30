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

# --- 3. LÓGICA DE METAS Y HORARIOS (BUCLE SEMANAL) ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = dias[hoy.weekday()]
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

plan_comida = {
    "Lunes": "🍳 Desayuno: Huevos + Avena | 🍗 Almuerzo: Pollo + Arroz + Aguacate | 🐟 Cena: Pescado + Ensalada",
    "Martes": "🥤 Desayuno: Batido Proteína + Banano | 🥩 Almuerzo: Carne Res + Pasta | 🍗 Cena: Pollo + Camote",
    "Miércoles": "🍳 Desayuno: Tortilla de claras | 🦃 Almuerzo: Pavo + Arroz Integral | 🐟 Cena: Atún + Ensalada Verde",
    "Jueves": "🥣 Desayuno: Yogur Griego + Frutos Secos | 🍗 Almuerzo: Pollo + Lentejas | 🍳 Cena: Huevos + Pan Integral",
    "Viernes": "🥣 Desayuno: Avena + Fruta (Carga Fútbol) | 🍝 Almuerzo: Pasta Carbonara | 🥤 Cena: Batido Post-Partido",
    "Sábado": "🥞 Desayuno: Pancakes Avena | 🐟 Almuerzo: Salmón/Pescado + Papas | 🍗 Cena: Pollo a la plancha",
    "Domingo": "🥗 Día Libre (Cumplir Macros base)"
}

plan_entreno = {
    "Lunes": "🍗 Piernas / Glúteos (Fuerza)",
    "Martes": "👕 Pecho / Tríceps / Hombros",
    "Miércoles": "🔙 Espalda / Bíceps",
    "Jueves": "🍗 Piernas / Glúteos (Hipertrofia)",
    "Viernes": "⚽ Fútbol / Cardio Explosivo",
    "Sábado": "👕 Torso Superior (Repetición)",
    "Domingo": "🛌 Descanso Activo / Estiramientos"
}

obj_act = st.session_state.u_obj
meta_k = 3200.0 if obj_act == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4
kcal_pasos = (st.session_state.get('steps', 0) / 1000) * 38

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.info(f"📅 **{dia_hoy}**\n\n💪 {plan_entreno[dia_hoy]}")
    st.divider()
    st.subheader("👣 Actividad")
    st.session_state.steps = st.number_input("Pasos hoy:", 0, 50000, st.session_state.get('steps', 0), step=500)
    if st.button("🔄 Reiniciar"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD PRINCIPAL ---
st.title(f"📊 Dashboard Nutricional")
p_act, k_act = 0.0, 0.0
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.date
        hoy_df = df[df['f'] == hoy.date()]
        k_act, p_act = hoy_df['kcal'].sum(), hoy_df['proteina'].sum()
except: pass

# Macros dinámicos (50% Carb, 25% Gras)
c_act, g_act = (k_act * 0.5) / 4, (k_act * 0.25) / 9

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.write(f"🔥 **Kcal:** {k_act:.0f}/{meta_k:.0f}")
    st.progress(min(k_act/meta_k, 1.0))
with c2:
    st.write(f"🍗 **Prot:** {p_act:.1f}/{meta_p:.0f}g")
    st.progress(min(p_act/meta_p, 1.0))
with c3:
    st.write(f"🍚 **Carb:** {c_act:.1f}/{meta_c:.0f}g")
    st.progress(min(c_act/meta_c, 1.0))
with c4:
    st.write(f"🥑 **Gras:** {g_act:.1f}/{meta_g:.0f}g")
    st.progress(min(g_act/meta_g, 1.0))

t1, t2, t3 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 HORARIO MAESTRO"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube tu plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    # CORRECCIÓN SINTAXIS LÍNEA 122:
                    img_raw = foto.read()
                    img_b64 = base64.b64encode(img_raw).decode()
                    prompt = "Responde SOLO: Nombre|Calorias|Proteina. Sin nada mas de texto."
                    payload = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(URL_AI, json=payload).json()
                    if 'candidates' in r:
                        texto = r['candidates'][0]['content']['parts'][0]['text'].strip()
                        partes = texto.split('|')
                        if len(partes) >= 3:
                            k_v = float(re.findall(r"\d+", partes[1])[0])
                            p_v = float(re.findall(r"\d+", partes[2])[0])
                            supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":partes[0].strip(), "kcal":k_v, "proteina":p_v, "semana":inicio_sem}).execute()
                            st.rerun()
                    else: st.warning("IA sin respuesta. Intenta otra vez.")
                except Exception as e: st.error(f"Error: {e}")
    with col_b:
        st.subheader("✍️ Manual")
        with st.form("manual"):
            c_m = st.text_input("Comida")
            p_m = st.number_input("Proteína (g)", 0.0)
            k_m = st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":c_m, "kcal":k_m, "proteina":p_m, "semana":inicio_sem}).execute()
                st.rerun()

with t2:
    st.plotly_chart(px.pie(values=[p_act*4, c_act*4, g_act*9], names=['Prot', 'Carb', 'Gras'], hole=0.4, template="plotly_dark", title="Distribución de Macros"), use_container_width=True)

with t3:
    st.subheader(f"🍽️ Alimentación: {dia_hoy}")
    st.success(plan_comida[dia_hoy])
    st.divider()
    st.subheader("🗓️ Cronograma Bucle Profesional")
    st.table(pd.DataFrame({"Día": dias, "Entreno": [plan_entreno[d] for d in dias], "Comidas": [plan_comida[d] for d in dias]}))
