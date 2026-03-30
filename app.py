import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# 1. SEGURIDAD
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa tus Secrets en Streamlit.")
    st.stop()

# 2. ESTILOS
st.markdown("""
<style>
    .pizarra-fondo { background-color: #262626; border: 8px solid #59402a; border-radius: 15px; padding: 25px; color: white; font-family: monospace; }
    .pizarra-titulo { color: #00FF41; text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid #444; margin-bottom: 20px; }
    .pizarra-valor { color: #00FF41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. SESIÓN Y REGISTRO
if 'usuario' not in st.session_state: st.session_state.usuario = None
if 'hoy_kcal' not in st.session_state: st.session_state.hoy_kcal = 0

if st.session_state.usuario is None:
    with st.form("login"):
        st.title("🦾 Jarvis Nutrición")
        nom = st.text_input("Nombre:")
        ps = st.number_input("Peso (kg):", value=75.0)
        al = st.number_input("Altura (cm):", value=170)
        if st.form_submit_button("ENTRAR"):
            st.session_state.usuario = {"nombre": nom, "peso": ps, "meta_kcal": ps * 35, "meta_p": ps * 2}
            st.rerun()
    st.stop()

u = st.session_state.usuario

# 4. DASHBOARD E INTERFAZ
with st.sidebar:
    st.header(f"Agente: {u['nombre'].upper()}")
    # La barra sube dinámicamente según lo consumido
    progreso = min(st.session_state.hoy_kcal / u['meta_kcal'], 1.0)
    st.write(f"🔥 Progreso diario: {int(progreso*100)}%")
    st.progress(progreso)
    if st.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

st.title("📈 Dashboard de Progreso")
col1, col2 = st.columns(2)
col1.metric("Meta Diaria", f"{int(u['meta_kcal'])} Kcal")
col2.metric("Consumido", f"{int(st.session_state.hoy_kcal)} Kcal")

# 5. REGISTRO DUAL (FOTO O TEXTO)
st.divider()
st.subheader("🍽️ Registrar Comida")
opcion = st.radio("Método de registro:", ["Cámara/Foto", "Escrito (Manual)"])

datos_comida = None

if opcion == "Cámara/Foto":
    foto = st.file_uploader("Sube tu plato", type=["jpg", "png", "jpeg"])
    if foto:
        img_64 = base64.b64encode(foto.read()).decode('utf-8')
        if st.button("🔍 Analizar Foto"):
            with st.spinner("Jarvis analizando..."):
                payload = {"contents": [{"parts": [{"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"}, {"inline_data": {"mime_type": "image/jpeg", "data": img_64}}]}]}
                try:
                    r = requests.post(URL_AI, json=payload).json()
                    res = r['candidates'][0]['content']['parts'][0]['text'].split('|')
                    datos_comida = {"nombre": res[0], "kcal": float(res[1]), "p": res[2], "c": res[3], "g": res[4]}
                except: st.error("Error de IA")

else:
    with st.form("manual"):
        n_m = st.text_input("¿Qué comiste?")
        k_m = st.number_input("Calorías estimadas:", min_value=0)
        p_m = st.text_input("Proteína (g):", "0")
        if st.form_submit_button("Registrar Manualmente"):
            datos_comida = {"nombre": n_m, "kcal": float(k_m), "p": p_m, "c": "0", "g": "0"}

# 6. GUARDAR Y MOSTRAR PIZARRA
if datos_comida:
    # Guardar en Supabase
    try:
        supabase.table('registros_comida').insert({
            "usuario": u['nombre'],
            "comida": datos_comida['nombre'],
            "kcal": datos_comida['kcal'],
            "proteina": datos_comida['p']
        }).execute()
        st.session_state.hoy_kcal += datos_comida['kcal']
        st.success("✅ Guardado en sistema")
    except: st.warning("No se pudo guardar en DB, pero se sumó a tu sesión.")

    # Mostrar Pizarra
    st.markdown(f"""
    <div class="pizarra-fondo">
        <div class="pizarra-titulo">{datos_comida['nombre'].upper()}</div>
        <p>🔥 CALORÍAS: <span class="pizarra-valor">{datos_comida['kcal']}</span></p>
        <p>🍗 PROTEÍNA: <span class="pizarra-valor">{datos_comida['p']}</span></p>
    </div>
    """, unsafe_allow_html=True)
    st.button("Actualizar barra 🔄")

# Gráfica de peso corregida
st.divider()
st.subheader("⚖️ Evolución de Peso")
df_peso = pd.DataFrame({
    'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'], 
    'Kg': [90, 87, 88, 85, 84, 86, 78] # Lista cerrada correctamente
})
st.plotly_chart(px.area(df_peso, x='Mes', y='Kg', template="plotly_dark", color_discrete_sequence=['#00FF41']))
