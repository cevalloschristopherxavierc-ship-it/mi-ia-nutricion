import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered")

if 'paso' not in st.session_state:
    st.session_state.paso = 5 # Directo al grano

# --- DASHBOARD ---
st.markdown("# Resumen Diario (63kg)")
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
        with st.spinner("🤖 Jarvis probando modelos disponibles..."):
            # LISTA DE MODELOS A PROBAR (Del más nuevo al más compatible)
            modelos_a_probar = [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro-vision"
            ]
            
            exito = False
            for mod in modelos_a_probar:
                try:
                    # Probamos con la URL v1 estable
                    url = f"https://generativelanguage.googleapis.com/v1/models/{mod}:generateContent?key={API_KEY}"
                    
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
                        st.success(f"✅ ¡Funcionó con el modelo {mod}!")
                        st.info(f"Detección: {res}")
                        exito = True
                        break # Salimos del bucle si funciona
                except:
                    continue # Si falla uno, prueba el siguiente
            
            if not exito:
                st.error("❌ Ningún modelo de Google respondió.")
                st.json(data) # Mostramos el último error recibido

if st.button("🔄 Reiniciar"):
    st.rerun()
