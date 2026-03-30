import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")

# --- LÓGICA DE ESTADO ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1

# --- PANTALLA DE INICIO ---
if st.session_state.paso == 1:
    st.markdown("# 🥗 Configuración FitIA")
    st.info("Perfil: 170cm | 63kg | Ganar Masa Muscular")
    if st.button("Ir al Resumen y Escáner ✨"):
        st.session_state.paso = 5
        st.rerun()

# --- DASHBOARD Y ESCÁNER ---
elif st.session_state.paso == 5:
    st.markdown("# Resumen Diario")
    
    # Macros optimizados para tus 63kg (Portoviejo Team!)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calorías", "2450")
    c2.metric("Proteína", "138g")
    c3.metric("Carbos", "285g")
    c4.metric("Grasas", "57g")

    st.divider()
    f = st.file_uploader("📸 Sube tu plato", type=["jpg", "jpeg", "png"])
    
    if f:
        img_bytes = f.read()
        st.image(img_bytes, use_container_width=True)
        
        if st.button("🔍 Analizar Plato"):
            with st.spinner("🤖 Jarvis conectando a la versión estable..."):
                try:
                    # CAMBIO CLAVE: Usamos /v1/ en lugar de /v1beta/
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    
                    b64_img = base64.b64encode(img_bytes).decode('utf-8')
                    
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
                                {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                            ]
                        }]
                    }
                    
                    r = requests.post(url, json=payload)
                    data = r.json()
                    
                    if 'candidates' in data:
                        res = data['candidates'][0]['content']['parts'][0]['text']
                        st.success(f"Detección: {res}")
                    else:
                        st.error("Error de respuesta:")
                        st.json(data)
                except Exception as e:
                    st.error(f"Error técnico: {e}")

    if st.button("🔄 Reiniciar"):
        st.session_state.paso = 1
        st.rerun()
