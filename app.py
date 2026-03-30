import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered", page_icon="🥗")

# Estilo visual de la App
st.markdown("# 🥗 Jarvis Nutrición Pro")
st.info("📍 Portoviejo | 👤 170cm | ⚖️ 63kg")

# --- ESCÁNER ---
f = st.file_uploader("📸 Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True, caption="Plato listo para análisis")
    
    if st.button("🔍 ANALIZAR MACROS"):
        with st.spinner("🤖 Jarvis activando motor 1.5-Flash-8B..."):
            try:
                # Usamos el modelo 1.5-flash-8b (El más estable de tu lista)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={API_KEY}"
                
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la comida. Responde estrictamente: Nombre|Kcal|Prot|Carb|Gras"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                        ]
                    }]
                }
                
                # Petición directa
                r = requests.post(url, json=payload)
                data = r.json()
                
                if 'candidates' in data:
                    texto = data['candidates'][0]['content']['parts'][0]['text']
                    stats = texto.split('|')
                    
                    if len(stats) >= 5:
                        st.balloons() # ¡Celebración!
                        st.success(f"🍴 Plato detectado: **{stats[0]}**")
                        
                        # Columnas para los Macros
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("🔥 Kcal", stats[1])
                        c2.metric("🍗 Prot", f"{stats[2]}g")
                        c3.metric("🍚 Carb", f"{stats[3]}g")
                        c4.metric("🥑 Gras", f"{stats[4]}g")
                        
                        st.divider()
                        st.caption(" Jarvis está listo para ayudarte con tu hipertrofia.")
                    else:
                        st.warning(f"Respuesta inesperada: {texto}")
                
                elif 'error' in data:
                    if data['error']['code'] == 429:
                        st.warning("⏳ Google sigue procesando tu nueva cuota. Espera 30 segundos exactos y dale al botón de nuevo.")
                    else:
                        st.error(f"Error {data['error']['code']}: {data['error']['message']}")
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")

if st.button("🔄 Reiniciar"):
    st.rerun()
