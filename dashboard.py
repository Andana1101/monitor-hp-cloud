import time
import pandas as pd
import streamlit as st
import requests

# URL API Cloud kamu
# Nanti kita simpan URL-nya di "Secrets" biar aman
API_URL = st.secrets["API_URL"]

st.set_page_config(page_title="Cloud Monitor", page_icon="☁️", layout="centered")

st.title("☁️ Cloud Device Monitor")

placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # Minta data ke API PythonAnywhere
            response = requests.get(f"{API_URL}/get_metrics", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    st.info("Menunggu data masuk dari HP...")
                else:
                    for d in data:
                        # Tentukan warna status
                        status_color = "🟢" if d['is_online'] else "🔴"
                        status_text = "ONLINE" if d['is_online'] else "OFFLINE"
                        
                        with st.expander(f"{status_color} {d['device_name']} ({status_text})", expanded=True):
                            c1, c2, c3 = st.columns(3)
                            c1.metric("RAM", f"{d['ram']}%")
                            c2.metric("Storage", f"{d['disk']}%")
                            
                            icon = "⚡" if d['is_plugged'] else "🔋"
                            c3.metric("Battery", f"{d['battery']}% {icon}")
                            
                            st.caption(f"Last Seen: {d['last_seen']}")
            else:
                st.error("Gagal konek ke API Server.")
                
        except Exception as e:
            # Error handling kalau API mati/internet putus
            st.error(f"Koneksi Terputus: {e}")
            
    time.sleep(10) # Refresh tiap 10 detik