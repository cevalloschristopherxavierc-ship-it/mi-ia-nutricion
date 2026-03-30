import streamlit as st
import requests, base64, re, pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- NÚCLEO XAVIER (63KG - DETALLES BLINDADOS) ---
st.set_page_config(page_title="Jarvis OS | Xavier", layout="wide", page_icon="🦾")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- SESIÓN ---
if 'u_nom' not in st.session_state:
    st.session_state.u_nom, st.session_state.u_pes = "Xavier", 63.0
    st.session_state.h2o = 0.0

# --- ESCÁNER REFORZADO (SOLUCIÓN AL 404) ---
st.header(f"📊 Panel de Control | {st.session_state.u_nom}")
c1, c2 = st.columns(2)

with c1:
    st.subheader("📸 Escáner IA (V1-PRO)")
    up = st.file_uploader("Foto", type=["jpg","png","jpeg"])
    if up and st.button("🔍 ANALIZAR"):
        with st.spinner("🤖 Jarvis forzando conexión..."):
            try:
                img_64 = base64.b64encode(up.read()).decode()
                key = st.secrets["GEMINI_API_KEY"]
                # CAMBIO A MODELO PRO PARA EVITAR EL 404 DEL FLASH
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={key}"
                
                payload = {"contents":[{"parts":[{"text":"Responde solo: Comida, Kcal, Proteina"},{"inline_data":{"mime_type":"image/jpeg","data":img_64}}]}]}
                r = requests.post(url, json=payload, timeout=30)
                
                if r.status_code == 200:
                    txt = r.json()['candidates'][0]['content']['parts'][0]['text']
                    nums = re.findall(r"\d+", txt)
                    if len(nums) >= 2:
                        supabase.table('registros_comida').insert({
                            "usuario": st.session_state.u_nom, "comida": "IA_Scan",
                            "kcal": float(nums[0]), "proteina": float(nums[1]),
                            "semana": datetime.now().strftime('%Y-%m-%d')
                        }).execute()
                        st.success("✅ ¡Éxito! Datos guardados.")
                        st.rerun()
                else:
                    st.error(f"🔴 Error {r.status_code}: El servidor de Google sigue rechazando la ruta.")
                    st.info("Sugerencia: Revisa si en Google AI Studio tienes habilitado el modelo 'Gemini 1.5 Pro'.")
            except: st.error("Fallo de red.")

with c2:
    st.subheader("✍️ Registro Manual (100% Funcional)")
    # (El código del formulario manual que ya sabemos que te funciona va aquí)
    with st.form("f_man", clear_on_submit=True):
        n = st.text_input("Comida")
        k = st.number_input("Kcal", 0.0)
        p = st.number_input("Prot", 0.0)
        if st.form_submit_button("💾 GUARDAR"):
            supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom,"comida":n,"kcal":k,"proteina":p,"semana":datetime.now().strftime('%Y-%m-%d')}).execute()
            st.rerun()
