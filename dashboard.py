import time
import pandas as pd
import streamlit as st
import requests
import plotly.graph_objects as go

# --- CONFIG ---
st.set_page_config(page_title="Synthetic Monitoring Mobile Device", page_icon="⚡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #333;
        border-radius: 10px;
    }
    /* Styling khusus buat Metric Card Battery */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- API URL ---
# Kita pakai Hardcode biar langsung jalan di Cloud tanpa setting Secrets
API_URL = "https://andana0411.pythonanywhere.com"

st.title("Synthetic Monitoring Mobile Device")
st.caption(f"Server Node: {API_URL}")

# --- HELPER: BIKIN DONUT CHART (Cuma buat RAM & Storage) ---
def create_donut(value, label, color):
    remaining = 100 - value
    fig = go.Figure(data=[go.Pie(
        labels=['Used', 'Free'],
        values=[value, remaining],
        hole=.7,
        marker_colors=[color, '#262730'],
        textinfo='none',
        hoverinfo='label+percent'
    )])
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=140,
        annotations=[dict(text=f"{value}%", x=0.5, y=0.5, font_size=18, showarrow=False)]
    )
    return fig

placeholder = st.empty()
loop_counter = 0

while True:
    with placeholder.container():
        loop_counter += 1
        try:
            # Ambil Data
            response = requests.get(f"{API_URL}/get_metrics", timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    st.info("📡 Waiting for device signal...")
                else:
                    for d in data:
                        dev_id = d['device_id']
                        status_dot = "🟢" if d['is_online'] else "🔴"
                        status_txt = "ONLINE" if d['is_online'] else "OFFLINE"
                        
                        with st.expander(f"{status_dot} {d['device_name']} ({status_txt})", expanded=True):
                            
                            col1, col2, col3 = st.columns(3)
                            
                            # --- 1. RAM (Pie Chart) ---
                            with col1:
                                st.markdown("<div style='text-align: center; color: #aaa; margin-bottom: 5px;'>RAM Usage</div>", unsafe_allow_html=True)
                                st.plotly_chart(
                                    create_donut(d['ram'], "RAM", "#636EFA"), 
                                    use_container_width=True, 
                                    key=f"ram_{dev_id}_{loop_counter}"
                                )
                                
                            # --- 2. STORAGE (Pie Chart) ---
                            with col2:
                                st.markdown("<div style='text-align: center; color: #aaa; margin-bottom: 5px;'>Storage</div>", unsafe_allow_html=True)
                                st.plotly_chart(
                                    create_donut(d['disk'], "Storage", "#EF553B"), 
                                    use_container_width=True,
                                    key=f"disk_{dev_id}_{loop_counter}"
                                )
                                
                            # --- 3. BATTERY (Classic Style) ---
                            with col3:
                                batt_val = d.get('battery', 0)
                                is_plugged = d.get('is_plugged', False)
                                icon = "⚡" if is_plugged else "🔋"
                                st.metric("Battery Level", f"{batt_val}% {icon}")
                                st.progress(min(batt_val / 100, 1.0))
                                status_cas = "Charging..." if is_plugged else "On Battery"
                                st.caption(f"Status: {status_cas}")

                            st.divider()
                            st.caption(f"Last Seen: {d['last_seen']}")
                            
                            # --- CHART AREA (Line Chart Classic) ---
                            st.subheader("📈 Performance Trend")
                            try:
                                hist_res = requests.get(f"{API_URL}/get_history/{d['device_id']}")
                                if hist_res.status_code == 200:
                                    hist_data = hist_res.json()
                                    if len(hist_data) > 2:
                                        df = pd.DataFrame(hist_data)
                                        df = df.tail(30) # Ambil 30 data terakhir
                                        df = df.set_index('time')
                                        
                                        st.line_chart(
                                            df[['ram', 'battery']], 
                                            color=["#636EFA", "#00CC96"], 
                                            height=250
                                        )
                            except:
                                pass
            else:
                st.error("API Error")
                
        except Exception as e:
            st.error(f"Connecting... {e}")
            
    time.sleep(5)
