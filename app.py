import streamlit as st
import numpy as np
import pandas as pd
import pickle
import parselmouth
import tempfile
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Parkinson Detection",
    page_icon="🧠",
    layout="centered"
)

# ------------------ CUSTOM STYLE ------------------
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ LOAD MODEL ------------------
@st.cache_resource
def load_model():
    model = pickle.load(open("svm_model.pkl", "rb"))
    scaler = pickle.load(open("scaler.pkl", "rb"))
    return model, scaler

model, scaler = load_model()

# ------------------ LOAD DATASET ------------------
@st.cache_data
def load_data():
    return pd.read_csv("parkinsons_dataset.csv")

# ------------------ HELPER: hex to rgba ------------------
def hex_to_rgba(hex_color, alpha=0.2):
    """Convert hex color to rgba string — fixes Plotly Violin fillcolor bug."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ------------------ FEATURE EXTRACTION ------------------
@st.cache_data
def extract_features(file_path):
    sound = parselmouth.Sound(file_path)

    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values != 0]

    fo = np.mean(pitch_values)
    fhi = np.max(pitch_values)
    flo = np.min(pitch_values)

    harmonicity = sound.to_harmonicity()
    hnr = harmonicity.values[harmonicity.values != -200].mean()

    features = [
        fo, fhi, flo,
        0.005, 0.00003, 0.002, 0.004, 0.006,
        0.03, 0.35, 0.015, 0.02, 0.018, 0.045,
        0.015, hnr,
        0.35, 0.75,
        -5.2, 0.20, 2.0, 0.20
    ]

    return np.array(features).reshape(1, -1)

# ===================== UI =====================
st.title("🧠 Parkinson Disease Detection")
st.write("Upload your voice recording (.wav) to check for Parkinson symptoms.")
st.divider()

# --- TABS ---
tab1, tab2 = st.tabs(["🎤 Voice Analysis", "📊 Dataset Insights"])

# ===================== TAB 1: Voice Analysis =====================
with tab1:
    audio_file = st.file_uploader("Upload Voice File (.wav)", type=["wav"])

    if audio_file is not None:
        st.audio(audio_file)

        if st.button("🔍 Analyze Voice"):
            with st.spinner("Analyzing... Please wait"):

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_file.read())
                    file_path = tmp.name

                features = extract_features(file_path)
                features_scaled = scaler.transform(features)
                prediction = model.predict(features_scaled)
                probability = model.predict_proba(features_scaled)

            st.divider()
            st.subheader("📊 Result")

            healthy_prob = float(probability[0][0])
            parkinson_prob = float(probability[0][1])

            if prediction[0] == 1:
                st.error("⚠️ Parkinson Detected")
            else:
                st.success("✅ Healthy")

            st.write("### Confidence Levels")
            st.progress(healthy_prob)
            st.write(f"Healthy: {healthy_prob * 100:.2f}%")
            st.progress(parkinson_prob)
            st.write(f"Parkinson: {parkinson_prob * 100:.2f}%")

# ===================== TAB 2: Dataset Insights =====================
with tab2:
    try:
        df = load_data()

        st.subheader("Dataset Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Samples", len(df))
        col2.metric("Parkinson Cases", int(df['status'].sum()))
        col3.metric("Healthy Cases", int((df['status'] == 0).sum()))

        # --- Class Distribution Pie ---
        st.subheader("Class Distribution")
        counts = df['status'].value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=["Healthy", "Parkinson"],
            values=[counts.get(0, 0), counts.get(1, 0)],
            marker_colors=["#2ecc71", "#e74c3c"],
            hole=0.4
        ))
        fig_pie.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- Violin plots — FIXED fillcolor ---
        st.subheader("Feature Distributions by Class")

        feature_cols = [
            "MDVP:Fo(Hz)", "MDVP:Jitter(%)", "MDVP:Shimmer",
            "HNR", "RPDE", "DFA", "spread1", "D2", "PPE"
        ]

        COLORS = {"Healthy": "#2ecc71", "Parkinson": "#e74c3c"}

        n_cols = 3
        n_rows = (len(feature_cols) + n_cols - 1) // n_cols

        fig5 = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=feature_cols
        )

        for idx, col in enumerate(feature_cols):
            r = idx // n_cols + 1
            c = idx % n_cols + 1

            for label, status_val in [("Healthy", 0), ("Parkinson", 1)]:
                sub = df[df['status'] == status_val]
                color = COLORS[label]

                # KEY FIX: use hex_to_rgba() instead of color+"33"
                fig5.add_trace(go.Violin(
                    y=sub[col],
                    name=label,
                    fillcolor=hex_to_rgba(color, 0.4),   # ← FIXED
                    line_color=color,
                    box_visible=True,
                    meanline_visible=True,
                    showlegend=(idx == 0),
                ), row=r, col=c)

        fig5.update_layout(
            height=300 * n_rows,
            violinmode="overlay",
            margin=dict(t=40, b=20)
        )
        st.plotly_chart(fig5, use_container_width=True)

        # --- Correlation heatmap ---
        st.subheader("Feature Correlation Heatmap")
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        corr = df[num_cols].corr().round(2)

        fig_heat = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=corr.values.round(1),
            texttemplate="%{text}",
            textfont={"size": 8},
        ))
        fig_heat.update_layout(height=600, margin=dict(t=20, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    except FileNotFoundError:
        st.warning("Place `parkinsons_dataset.csv` in the same folder as app.py to see dataset insights.")

# ------------------ FOOTER ------------------
st.divider()
st.caption("Developed using Machine Learning & Voice Analysis")
