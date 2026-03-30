import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

st.set_page_config(page_title="Jarvis Pro", layout="centered")

# --- MEMORIA ---
if 'historial' not in st.session_state: st.session_state.historial = []
if 'total_prot' not in st.session_state: st.session_state.total_prot = 0.0

# --- INTERFAZ ---
st.title("💪 Jarvis: Modo Hipertrofia")
st.write(f"### Proteína: {st.session_state.total_prot:.1f}g / 126.0g")
st.progress(min(st.session_state.total_prot / 126.0, 1.0))

f = st.file_uploader("📸 Escanea tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 ANALIZAR Y GUARDAR"):
        with st.spinner("🤖 Calculando..."):
            try:
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {"contents": [{"parts": [
                    {"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                ]}]}
                
                r = requests.post(URL, json=payload)
                data = r.json()
                
                if 'candidates' in data:
                    res = data['candidates'][0]['content']['parts'][0]['text']
                    s = res.split('|')
                    if len(s) >= 5:
                        # Limpiar y extraer proteína
                        p_val = float(s[2].lower().replace('g','').replace('prot:','').strip())
                        
                        # Guardar Registro
                        item = {"hora": datetime.now().strftime("%H:%M"), "nombre": s[0], "prot": p_val, "kcal": s[1]}
                        st.session_state.historial.append(item)
                        st.session_state.total_prot += p_val
                        
                        st.balloons()
                        st.success(f"✅ {s[0]} guardado")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Kcal", s[1]); c2.metric("Prot", f"{p_val}g"); c3.metric("Carb", s[3]); c4.metric("Gras", s[4])
                else:
                    st.error("Error en API. Revisa tu Key.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- HISTORIAL ---
st.divider()
st.subheader("📝 Hoy has comido:")
for i in reversed(st.session_state.historial):
    st.write(f"🍴 **{i['nombre']}** ({i['hora']}) — {i['prot']}g Prot | {i['kcal']} Kcal")

if st.button("🗑️ Reset"):
    st.session_state.historial = []; st.session_state.total_prot = 0.0; st.rerun()
