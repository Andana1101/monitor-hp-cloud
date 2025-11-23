import time
import pandas as pd
import streamlit as st
import requests

# --- KONFIGURASI & CSS ---
try:
    API_URL = st.secrets["API_URL"]
except KeyError:
    st.error("❌ API_URL belum disetting di Secrets Streamlit Cloud!")
    st.stop()

st.set_page_config(page_title="Cloud Monitor Pro", page_icon="☁️", layout="centered")

# Custom CSS biar tampilan Card Metrics lebih gelap dan elegan
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #262730; /* Warna latar gelap */
        border: 1px solid #404040;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricLabel"] {
        color: #b0b0b0; /* Warna label agak abu */
    }
</style>
""", unsafe_allow_html=True)

st.title("☁️ Cloud Device Monitor Pro")
st.caption(f"Server API: {API_URL}")

# Container untuk auto-refresh
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # --- 1. Ambil Data Status Terkini ---
            response = requests.get(f"{API_URL}/get_metrics", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    st.info("📡 Menunggu data masuk dari HP...")
                else:
                    # Loop untuk setiap device yang terdaftar
                    for d in data:
                        # Tentukan status dan warna
                        is_online = d.get('is_online', False)
                        status_icon = "🟢" if is_online else "🔴"
                        status_text = "ONLINE" if is_online else "OFFLINE"
                        
                        # Buat Expander (Dropdown) per Device
                        with st.expander(f"{status_icon} {d['device_name']} ({status_text})", expanded=True):
                            
                            # --- A. Metrics Card ---
                            c1, c2, c3 = st.columns(3)
                            
                            with c1:
                                ram_val = d.get('ram', 0)
                                st.metric("🧠 RAM Usage", f"{ram_val:.1f}%")
                                st.progress(min(ram_val / 100, 1.0))
                                
                            with c2:
                                disk_val = d.get('disk', 0)
                                st.metric("💾 Storage", f"{disk_val:.1f}%")
                                st.progress(min(disk_val / 100, 1.0))
                                
                            with c3:
                                batt_val = d.get('battery', 0)
                                is_plugged = d.get('is_plugged', False)
                                icon = "⚡" if is_plugged else "🔋"
                                st.metric("Battery", f"{batt_val:.1f}% {icon}")
                                st.progress(min(batt_val / 100, 1.0))
                            
                            st.caption(f"🕒 Last Seen: {d.get('last_seen')}")

                            # --- B. BAGIAN BARU: GRAFIK PRO ---
                            st.divider()
                            st.subheader("📈 Live Trend Chart")
                            
                            # Minta data history ke API baru
                            try:
                                device_id = d.get('device_id')
                                hist_res = requests.get(f"{API_URL}/get_history/{device_id}", timeout=5)
                                
                                if hist_res.status_code == 200:
                                    hist_data = hist_res.json()
                                    
                                    if len(hist_data) > 1:
                                        # Ubah JSON ke Pandas DataFrame biar gampang bikin grafik
                                        df_chart = pd.DataFrame(hist_data)
                                        # Set kolom waktu jadi index (sumbu X)
                                        df_chart = df_chart.set_index('time')
                                        
                                        # Tampilkan grafik garis (RAM & Battery)
                                        st.line_chart(
                                            df_chart[['ram', 'battery']], 
                                            height=250,
                                            color=["#FF5733", "#33FF57"] # Custom warna (Opsional: Merah=RAM, Hijau=Batre)
                                        )
                                    else:
                                        st.caption("Menunggu lebih banyak data untuk menampilkan grafik...")
                                else:
                                    st.warning(f"Gagal mengambil history (API: {hist_res.status_code})")
                            except Exception as e:
                                st.error(f"Gagal memuat grafik: {e}")
                            # ----------------------------------

            else:
                st.error(f"⚠️ Gagal konek ke Server API (Status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Tidak bisa menghubungi Server API Cloud. Cek PythonAnywhere.")
        except Exception as e:
            st.error(f"Unexpected Error: {e}")
    # Refresh dashboard setiap 5 detik
    time.sleep(5)
