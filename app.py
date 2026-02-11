import streamlit as st
import joblib
import numpy as np

# Page config
st.set_page_config(
    page_title="Asthma Risk Prediction",
    page_icon="🫁",
    layout="centered"
)

# Load model (model is in SAME folder as app.py)
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "asthma_model.pkl")
model = joblib.load(MODEL_PATH)



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
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="big-title">🫁 Asthma Risk Prediction System</div>', unsafe_allow_html=True)
st.write("Enter patient vitals to predict asthma risk")

# Input card
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    hr = st.number_input("❤️ Heart Rate (bpm)", 30, 200, 80)
    spo2 = st.number_input("🩸 SpO₂ (%)", 80, 100, 97)
    rr = st.number_input("🌬 Respiration Rate (breaths/min)", 5, 50, 18)

    st.markdown('</div>', unsafe_allow_html=True)

# Predict
if st.button("🔍 Predict"):
    input_data = np.array([[hr, spo2, rr]])
    prediction = model.predict(input_data)[0]

    if prediction == 1:
        st.error("🚨 **Asthma Risk Detected!**")

        # 🔊 BUZZER SOUND (NO FILE NEEDED)
        st.components.v1.html("""
        <script>
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = context.createOscillator();
        oscillator.type = "square";
        oscillator.frequency.setValueAtTime(800, context.currentTime);
        oscillator.connect(context.destination);
        oscillator.start();
        setTimeout(() => oscillator.stop(), 600);
        </script>
        """, height=0)

    else:
        st.success("✅ **No Asthma Risk Detected**")

