import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")

# --- DASHBOARD (Simplificado para que funcione ya) ---
st.markdown("# 🥗 FitIA Pro: Resumen")

# Datos basados en tu perfil de 63kg
col1, col2, col3, col4 = st.columns(4)
col1.metric("Calorías", "2450 kcal")
col2.metric("Proteína", "138g")
col3.metric("Carbos", "285g")
col4.metric("Grasas", "57g")

st.
