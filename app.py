import streamlit as st
import joblib
import numpy as np
import requests
import os

# Page config
st.set_page_config(
    page_title="Asthma Risk Prediction",
    page_icon="🫁",
    layout="centered"
)

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "asthma_model.pkl")
model = joblib.load(MODEL_PATH)

# ThingSpeak credentials
CHANNEL_ID  = "3288047"
READ_API_KEY = "HW214U2VDZDPBLVJ"

# Custom CSS
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: bold;
    color: #ff4b4b;
    text-align: center;
}
.card {
    background-color: #f9f9f9;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}
.metric-box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    text-align: center;
}
.metric-value {
    font-size: 36px;
    font-weight: bold;
    color: #ff4b4b;
}
.metric-label {
    font-size: 14px;
    color: #666666;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="big-title">🫁 Asthma Risk Prediction System</div>',
            unsafe_allow_html=True)
st.write("")

# ── Tabs ──────────────────────────────────────────
tab1, tab2 = st.tabs(["🔴 Live Sensor", "✍️ Manual Input"])

# ══════════════════════════════════════════════════
# TAB 1 — LIVE SENSOR (ThingSpeak)
# ══════════════════════════════════════════════════
with tab1:
    st.subheader("📡 Live Readings from ESP32 Sensor")
    st.write("Readings update automatically from your wristband!")

    # Fetch from ThingSpeak
    def get_latest_readings():
        try:
            url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json?api_key={READ_API_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            hr   = float(data.get("field1", 0) or 0)
            spo2 = float(data.get("field2", 0) or 0)
            rr   = float(data.get("field3", 0) or 0)
            risk = int(float(data.get("field4", 0) or 0))
            return hr, spo2, rr, risk, True
        except Exception as e:
            return 0, 0, 0, 0, False

    # Refresh button
    if st.button("🔄 Refresh Readings"):
        st.rerun()

    # Auto refresh every 15 seconds
    st.write("*Auto-refreshes every 15 seconds*")

    hr_live, spo2_live, rr_live, risk_live, success = get_latest_readings()

    if not success:
        st.warning("⚠️ Could not connect to ThingSpeak. Check internet connection!")
    elif hr_live == 0:
        st.info("👆 Place finger on sensor to start reading!")
    else:
        # Show metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">❤️ {int(hr_live)}</div>
                <div class="metric-label">Heart Rate (bpm)</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">🩸 {int(spo2_live)}%</div>
                <div class="metric-label">SpO₂</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">🌬️ {int(rr_live)}</div>
                <div class="metric-label">Respiration Rate</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # ML Prediction on live data
        input_data = np.array([[hr_live, spo2_live, rr_live]])
        prediction = model.predict(input_data)[0]

        st.write("### 🤖 ML Model Prediction:")

        if prediction == 1:
            st.error("🚨 **Asthma Risk Detected!**")
            st.markdown("""
            **Possible causes:**
            - SpO₂ below 95% indicates low oxygen
            - High heart rate indicates stress
            - High respiration rate indicates breathing difficulty
            
            **Recommended action:** Consult a doctor immediately!
            """)
            # Buzzer sound
            st.components.v1.html("""
            <script>
            var ctx = new (window.AudioContext || window.webkitAudioContext)();
            var osc = ctx.createOscillator();
            osc.type = "square";
            osc.frequency.setValueAtTime(800, ctx.currentTime);
            osc.connect(ctx.destination);
            osc.start();
            setTimeout(() => osc.stop(), 800);
            </script>
            """, height=0)
        else:
            st.success("✅ **No Asthma Risk Detected — All vitals normal!**")

        # Risk level from hardware
        st.write("### 🔴 Hardware Risk Level:")
        if risk_live == 0:
            st.success("✅ NORMAL")
        elif risk_live == 1:
            st.warning("⚠️ MILD RISK")
        else:
            st.error("🚨 SEVERE RISK")

        # Show thresholds
        with st.expander("📊 View Normal Ranges"):
            st.markdown("""
            | Parameter | Normal Range | Your Value | Status |
            |---|---|---|---|
            | Heart Rate | 60-100 bpm | {} bpm | {} |
            | SpO₂ | 95-100% | {}% | {} |
            | Respiration Rate | 12-20 /min | {} /min | {} |
            """.format(
                int(hr_live),
                "✅" if 60 <= hr_live <= 100 else "⚠️",
                int(spo2_live),
                "✅" if spo2_live >= 95 else "⚠️",
                int(rr_live),
                "✅" if 12 <= rr_live <= 20 else "⚠️"
            ))

    # Auto refresh
    st.components.v1.html("""
    <script>
    setTimeout(function() {
        window.location.reload();
    }, 15000);
    </script>
    """, height=0)

# ══════════════════════════════════════════════════
# TAB 2 — MANUAL INPUT
# ══════════════════════════════════════════════════
with tab2:
    st.subheader("✍️ Manual Vital Signs Input")
    st.write("Enter patient vitals manually to predict asthma risk")

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        hr_m   = st.number_input("❤️ Heart Rate (bpm)", 30, 200, 80)
        spo2_m = st.number_input("🩸 SpO₂ (%)", 80, 100, 97)
        rr_m   = st.number_input("🌬 Respiration Rate (breaths/min)", 5, 50, 18)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔍 Predict"):
        input_data = np.array([[hr_m, spo2_m, rr_m]])
        prediction = model.predict(input_data)[0]

        if prediction == 1:
            st.error("🚨 **Asthma Risk Detected!**")
            st.components.v1.html("""
            <script>
            var ctx = new (window.AudioContext || window.webkitAudioContext)();
            var osc = ctx.createOscillator();
            osc.type = "square";
            osc.frequency.setValueAtTime(800, ctx.currentTime);
            osc.connect(ctx.destination);
            osc.start();
            setTimeout(() => osc.stop(), 600);
            </script>
            """, height=0)
        else:
            st.success("✅ **No Asthma Risk Detected**")
