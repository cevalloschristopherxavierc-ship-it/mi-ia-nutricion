import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# ==========================================
# 1. SEGURIDAD Y CONEXIÓN (SECRETS)
# ==========================================
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Error en Secrets. Revisa Streamlit Cloud.")
    st.stop()

# ==========================================
# 2. ANIMACIÓN DE CARGA (XAVIER CEVALLOS)
# ==========================================
if 'intro' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h1 style='text-align: center; color: #00FF41;'>🦾 JARVIS OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>SISTEMA DE BIOMETRÍA BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in
