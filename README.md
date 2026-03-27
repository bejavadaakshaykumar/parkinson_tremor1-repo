# 🧠 Parkinson's Voice Analytics Dashboard

An interactive Streamlit app for exploring, visualizing, and predicting Parkinson's disease from biomedical voice recordings using the **UCI Parkinson's Dataset**.

---

## ✨ Features

| Tab | What's inside |
|-----|--------------|
| 📊 **Overview** | Class distribution pie, recordings per patient, feature radar chart, full correlation heatmap |
| 🔬 **Feature Deep Dive** | Violin plots, box plots, scatter with marginals — grouped by Jitter / Shimmer / Frequency / Nonlinear / Noise |
| 🤖 **ML Model** | Random Forest (200 trees) · Accuracy, Precision, Recall, F1 · Confusion matrix · ROC curve · Feature importance |
| 🧬 **Predict** | Live interactive sliders → real-time prediction + probability gauge |
| 📋 **Data Explorer** | Searchable table, summary statistics, CSV download |

**UI Highlights:**
- Animated gradient hero banner
- Animated KPI cards with hover lift & colour accent bars
- Pulsing rainbow progress bar
- Zoom-in prediction result cards (green = healthy / red = Parkinson's)
- Clean white background throughout

---

## 🚀 Run Locally

```bash
git clone https://github.com/<your-username>/parkinsons-voice-analytics.git
cd parkinsons-voice-analytics

pip install -r requirements.txt

# Copy the dataset into the project root
cp /path/to/parkinsons_dataset.csv .

streamlit run app.py
```

---

## 🌐 Deploy on Streamlit Cloud

1. Push this repo to GitHub (include `app.py`, `requirements.txt`, `parkinsons_dataset.csv`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Choose repo · branch `main` · main file `app.py`
4. Click **Deploy** 🎉

---

## 📁 Repository Structure

```
parkinsons-voice-analytics/
├── app.py                      # Streamlit application
├── requirements.txt            # Python dependencies
├── parkinsons_dataset.csv      # UCI dataset (add manually)
└── README.md
```

---

## 📊 Dataset Features

| Group | Features |
|-------|---------|
| Fundamental Frequency | MDVP:Fo(Hz), Fhi(Hz), Flo(Hz) |
| Jitter | Jitter(%), Jitter(Abs), RAP, PPQ, DDP |
| Shimmer | Shimmer, Shimmer(dB), APQ3, APQ5, APQ, DDA |
| Noise Ratios | NHR, HNR |
| Nonlinear Dynamics | RPDE, DFA, spread1, spread2, D2, PPE |

**Target:** `status` — 1 = Parkinson's, 0 = Healthy

Source: [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/parkinsons)

---

> ⚠️ **Disclaimer:** This tool is for educational and research purposes only. It is not a clinical diagnostic tool.
