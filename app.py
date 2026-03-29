import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import warnings
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Parkinson's Voice Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main { background:#ffffff !important; }
[data-testid="stHeader"] { background:transparent !important; }
* { font-family:'Inter',sans-serif !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg,#0d1b2a 0%,#1b2d4f 55%,#162340 100%) !important;
}
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color:#f1f5f9 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label {
    color:#94a3b8 !important; font-size:11px;
    letter-spacing:.08em; text-transform:uppercase; font-weight:600;
}

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg,#0d1b2a 0%,#1e3a8a 45%,#7c3aed 100%);
    border-radius:24px; padding:48px 56px; margin-bottom:32px;
    position:relative; overflow:hidden;
    animation: fadeSlideDown .8s cubic-bezier(.22,1,.36,1) both;
    box-shadow: 0 24px 64px rgba(30,58,138,.25);
}
.hero::before {
    content:""; position:absolute; inset:0;
    background:radial-gradient(ellipse at 80% 20%,rgba(124,58,237,.35) 0%,transparent 60%);
}
.hero::after {
    content:""; position:absolute; right:-60px; top:-60px;
    width:260px; height:260px; border-radius:50%;
    background:rgba(255,255,255,.04);
}
.hero-emoji { font-size:3rem; display:block; margin-bottom:10px; animation:pulse 2.5s ease infinite; }
.hero-title { color:#fff; font-size:2.5rem; font-weight:900; margin:0 0 8px; letter-spacing:-.03em; }
.hero-sub   { color:#bfdbfe; font-size:1.05rem; margin:0; font-weight:400; }
.hero-badge {
    display:inline-block; margin-top:16px;
    background:rgba(255,255,255,.12); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,.2); border-radius:999px;
    padding:6px 18px; color:#e0f2fe; font-size:.8rem; font-weight:600;
    letter-spacing:.06em; text-transform:uppercase;
}

/* ── Pulse bar ── */
.pulse-bar {
    height:3px; border-radius:999px;
    background:linear-gradient(90deg,#6366f1,#8b5cf6,#06b6d4,#6366f1);
    background-size:300% 100%;
    animation:pulseSlide 3.5s linear infinite;
    margin:0 0 28px;
}
@keyframes pulseSlide { to { background-position:-300% 0; } }

/* ── KPI grid ── */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-bottom:28px; }
.kpi-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:18px;
    padding:24px 22px; box-shadow:0 4px 24px rgba(0,0,0,.06);
    animation:fadeUp .6s cubic-bezier(.22,1,.36,1) both;
    transition:transform .3s,box-shadow .3s; cursor:default;
    position:relative; overflow:hidden;
}
.kpi-card::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background:var(--accent,#6366f1);
    transform:scaleX(0); transform-origin:left;
    transition:transform .4s ease;
}
.kpi-card:hover::before { transform:scaleX(1); }
.kpi-card:hover { transform:translateY(-6px); box-shadow:0 16px 40px rgba(0,0,0,.12); }
.kpi-icon  { font-size:2rem; margin-bottom:10px; display:block; }
.kpi-label { font-size:10.5px; font-weight:700; letter-spacing:.1em;
             text-transform:uppercase; color:#94a3b8; margin-bottom:6px; }
.kpi-value { font-size:2.1rem; font-weight:900; color:#0f172a; line-height:1; }
.kpi-sub   { font-size:12px; color:#64748b; margin-top:6px; }

/* ── Section header ── */
.sec-hdr {
    display:flex; align-items:center; gap:10px;
    font-size:1.1rem; font-weight:800; color:#0f172a;
    margin:28px 0 14px; padding-bottom:12px;
    border-bottom:2px solid #ede9fe;
}

/* ── Chart card ── */
.chart-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:18px;
    padding:12px 16px 16px; box-shadow:0 4px 20px rgba(0,0,0,.05);
    animation:fadeUp .7s cubic-bezier(.22,1,.36,1) both;
    margin-bottom:18px; transition:box-shadow .3s;
}
.chart-card:hover { box-shadow:0 10px 36px rgba(99,102,241,.1); }

/* ── Prediction box ── */
.pred-box {
    border-radius:18px; padding:28px 32px; text-align:center;
    animation:zoomIn .5s cubic-bezier(.22,1,.36,1) both;
    margin-bottom:16px;
}
.pred-pos { background:linear-gradient(135deg,#fef2f2,#ffe4e6); border:2px solid #fca5a5; }
.pred-neg { background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:2px solid #86efac; }
.pred-title { font-size:1.6rem; font-weight:900; margin-bottom:8px; }
.pred-conf  { font-size:1rem; font-weight:500; color:#475569; }

/* ── Animations ── */
@keyframes fadeSlideDown {
    from { opacity:0; transform:translateY(-28px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(22px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes zoomIn {
    from { opacity:0; transform:scale(.9); }
    to   { opacity:1; transform:scale(1); }
}
@keyframes pulse {
    0%,100% { transform:scale(1); }
    50%      { transform:scale(1.08); }
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-weight:600; font-size:.88rem; color:#64748b;
    border-radius:10px 10px 0 0;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color:#7c3aed; border-bottom:3px solid #7c3aed;
}
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#f8fafc; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:999px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  DATA & MODEL
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv("parkinsons_dataset.csv")
    df["patient_id"] = df["name"].str.extract(r"(phon_R\d+_S\d+)")
    df["label"] = df["status"].map({1:"Parkinson's", 0:"Healthy"})
    return df

@st.cache_resource
def train_model(df):
    feats = [c for c in df.columns if c not in ["name","status","label","patient_id"]]
    X = df[feats].values
    y = df["status"].values
    sc = StandardScaler()
    Xs = sc.fit_transform(X)
    Xtr, Xte, ytr, yte = train_test_split(Xs, y, test_size=.2, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(Xtr, ytr)
    return clf, sc, feats, Xte, yte

df = load_data()
clf, sc, features, X_te, y_te = train_model(df)

JITTER_COLS    = ["MDVP:Jitter(%)","MDVP:Jitter(Abs)","MDVP:RAP","MDVP:PPQ","Jitter:DDP"]
SHIMMER_COLS   = ["MDVP:Shimmer","MDVP:Shimmer(dB)","Shimmer:APQ3","Shimmer:APQ5","MDVP:APQ","Shimmer:DDA"]
FREQ_COLS      = ["MDVP:Fo(Hz)","MDVP:Fhi(Hz)","MDVP:Flo(Hz)"]
NONLINEAR_COLS = ["RPDE","DFA","spread1","spread2","D2","PPE"]
RATIO_COLS     = ["NHR","HNR"]

PL  = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
           font=dict(family="Inter,sans-serif", color="#1e293b"),
           margin=dict(l=8,r=8,t=44,b=8))
PAL = {"Parkinson's":"#7c3aed","Healthy":"#10b981"}

def hex_to_rgba(hex_color, alpha=0.2):
    """Convert hex to rgba string — fixes Plotly Violin fillcolor bug."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧠 Parkinson's Analytics")
    st.markdown("---")
    st.markdown("#### 🎛️ Dashboard Filters")
    status_filter = st.multiselect(
        "Status", ["Parkinson's","Healthy"],
        default=["Parkinson's","Healthy"])
    patient_filter = st.multiselect(
        "Patient ID", sorted(df["patient_id"].unique()), default=[])
    st.markdown("---")
    st.markdown("#### 🔬 Feature Group")
    feat_group = st.selectbox("Explore group", [
        "Jitter (Frequency Variation)",
        "Shimmer (Amplitude Variation)",
        "Fundamental Frequency",
        "Nonlinear Dynamics",
        "Noise Ratios"])
    st.markdown("---")
    st.caption("UCI Parkinson's Voice Dataset\n195 samples · 32 patients · 22 features")

mask = df["label"].isin(status_filter)
if patient_filter:
    mask &= df["patient_id"].isin(patient_filter)
dff = df[mask].copy()

# ══════════════════════════════════════════════
#  HERO + PULSE BAR
# ══════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <span class="hero-emoji">🧠</span>
  <div class="hero-title">Parkinson's Voice Analytics</div>
  <div class="hero-sub">Biomedical voice signal analysis · 22 acoustic features · ML-powered diagnosis prediction</div>
  <span class="hero-badge">📊 195 Recordings · 32 Patients · UCI Dataset</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="pulse-bar"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  KPI CARDS
# ══════════════════════════════════════════════
total  = len(dff)
pk_cnt = int((dff["status"]==1).sum())
hl_cnt = int((dff["status"]==0).sum())
pk_pct = round(pk_cnt/total*100,1) if total else 0
avg_hnr= round(float(dff["HNR"].mean()),2) if total else 0

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card" style="--accent:#6366f1">
    <span class="kpi-icon">👥</span>
    <div class="kpi-label">Total Recordings</div>
    <div class="kpi-value">{total}</div>
    <div class="kpi-sub">voice samples in view</div>
  </div>
  <div class="kpi-card" style="--accent:#dc2626">
    <span class="kpi-icon">🔴</span>
    <div class="kpi-label">Parkinson's</div>
    <div class="kpi-value">{pk_cnt}</div>
    <div class="kpi-sub">{pk_pct}% of dataset</div>
  </div>
  <div class="kpi-card" style="--accent:#10b981">
    <span class="kpi-icon">🟢</span>
    <div class="kpi-label">Healthy</div>
    <div class="kpi-value">{hl_cnt}</div>
    <div class="kpi-sub">{round(100-pk_pct,1)}% of dataset</div>
  </div>
  <div class="kpi-card" style="--accent:#f59e0b">
    <span class="kpi-icon">🎙️</span>
    <div class="kpi-label">Avg HNR</div>
    <div class="kpi-value">{avg_hnr}</div>
    <div class="kpi-sub">Harmonics-to-Noise Ratio</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "🔬 Feature Deep Dive",
    "🤖 ML Model", "🧬 Predict", "📋 Data Explorer"])

# ── TAB 1: OVERVIEW ──────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        pie = dff["label"].value_counts().reset_index()
        pie.columns = ["Status","Count"]
        fig = px.pie(pie, names="Status", values="Count",
                     title="Class Distribution",
                     color="Status", color_discrete_map=PAL, hole=.52)
        fig.update_traces(textinfo="percent+label", pull=[0.04,0])
        fig.update_layout(**PL, legend=dict(orientation="h",y=-.1))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        pt = dff.groupby(["patient_id","label"])["status"].count().reset_index()
        pt.columns = ["Patient","Status","Recordings"]
        fig2 = px.bar(pt, x="Patient", y="Recordings", color="Status",
                      title="Recordings per Patient",
                      color_discrete_map=PAL, barmode="stack")
        fig2.update_layout(**PL, xaxis_tickangle=45, xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Radar chart
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    key_feats = ["MDVP:Fo(Hz)","HNR","RPDE","DFA","PPE","spread1","spread2","D2"]
    h_vals = dff[dff["status"]==0][key_feats].mean().tolist()
    p_vals = dff[dff["status"]==1][key_feats].mean().tolist()
    mms = MinMaxScaler()
    mat = mms.fit_transform(np.array([h_vals, p_vals]).T).T
    h_n, p_n = mat[0].tolist() + [mat[0][0]], mat[1].tolist() + [mat[1][0]]
    cats = key_feats + [key_feats[0]]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatterpolar(r=h_n, theta=cats, fill="toself",
        name="Healthy", line_color="#10b981", fillcolor="rgba(16,185,129,.15)"))
    fig3.add_trace(go.Scatterpolar(r=p_n, theta=cats, fill="toself",
        name="Parkinson's", line_color="#7c3aed", fillcolor="rgba(124,58,237,.15)"))
    fig3.update_layout(**PL, title="Feature Radar — Normalised Mean Comparison",
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        legend=dict(orientation="h",y=-.12))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Correlation heatmap
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    num_cols = [c for c in dff.columns if dff[c].dtype in [np.float64,np.int64] and c!="status"]
    corr = dff[num_cols+["status"]].corr()
    fig4 = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                     title="Feature Correlation Matrix", aspect="auto", zmin=-1, zmax=1)
    fig4.update_layout(**PL, height=520)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 2: FEATURE DEEP DIVE ─────────────────
with tab2:
    group_map = {
        "Jitter (Frequency Variation)":  JITTER_COLS,
        "Shimmer (Amplitude Variation)": SHIMMER_COLS,
        "Fundamental Frequency":         FREQ_COLS,
        "Nonlinear Dynamics":            NONLINEAR_COLS,
        "Noise Ratios":                  RATIO_COLS,
    }
    cols_sel = group_map[feat_group]

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    n = len(cols_sel)
    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols
    fig5 = make_subplots(rows=nrows, cols=ncols,
                         subplot_titles=cols_sel, vertical_spacing=.12)
    for idx, col in enumerate(cols_sel):
        r, c = divmod(idx, ncols)
        for lbl, color in PAL.items():
            sub = dff[dff["label"]==lbl]
            fig5.add_trace(go.Violin(
                y=sub[col], name=lbl, fillcolor=hex_to_rgba(color, 0.2), line_color=color,
                box_visible=True, meanline_visible=True, showlegend=(idx==0),
            ), row=r+1, col=c+1)
    fig5.update_layout(**PL, title=f"{feat_group} — Distributions by Status",
                       height=380*nrows, violingap=.3)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    melt = dff[cols_sel+["label"]].melt(id_vars="label", var_name="Feature", value_name="Value")
    fig6 = px.box(melt, x="Feature", y="Value", color="label",
                  title=f"{feat_group} — Grouped Box Plot",
                  color_discrete_map=PAL, points="outliers")
    fig6.update_layout(**PL)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if len(cols_sel) >= 2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        pair_x = st.selectbox("X axis", cols_sel, index=0)
        pair_y = st.selectbox("Y axis", cols_sel, index=min(1,len(cols_sel)-1))
        fig7 = px.scatter(dff, x=pair_x, y=pair_y, color="label",
                          marginal_x="histogram", marginal_y="histogram",
                          color_discrete_map=PAL, opacity=.75,
                          title=f"{pair_x} vs {pair_y}")
        fig7.update_layout(**PL)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 3: ML MODEL ──────────────────────────
with tab3:
    y_pred = clf.predict(X_te)
    y_prob = clf.predict_proba(X_te)[:,1]
    report = classification_report(y_te, y_pred, output_dict=True)
    acc    = round(report["accuracy"]*100, 2)

    c1,c2,c3,c4 = st.columns(4)
    metrics = [
        ("Accuracy",  f"{acc}%",                                           "#6366f1"),
        ("Precision", f"{round(report['1']['precision']*100,2)}%",         "#10b981"),
        ("Recall",    f"{round(report['1']['recall']*100,2)}%",            "#f59e0b"),
        ("F1-Score",  f"{round(report['1']['f1-score']*100,2)}%",         "#7c3aed"),
    ]
    for col, (label, val, color) in zip([c1,c2,c3,c4], metrics):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{color}">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value" style="color:{color}">{val}</div>
              <div class="kpi-sub">Random Forest · 200 trees</div>
            </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        cm = confusion_matrix(y_te, y_pred)
        fig8 = px.imshow(cm, text_auto=True,
                         x=["Pred Healthy","Pred Parkinson's"],
                         y=["Act Healthy","Act Parkinson's"],
                         color_continuous_scale="Purples",
                         title="Confusion Matrix")
        fig8.update_layout(**PL, height=340)
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fpr, tpr, _ = roc_curve(y_te, y_prob)
        roc_auc = auc(fpr, tpr)
        fig9 = go.Figure()
        fig9.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines",
            name=f"ROC (AUC={roc_auc:.3f})",
            line=dict(color="#7c3aed", width=3)))
        fig9.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
            line=dict(color="#94a3b8", dash="dash"), showlegend=False))
        fig9.update_layout(**PL, title="ROC Curve",
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate", height=340)
        st.plotly_chart(fig9, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    imp = pd.DataFrame({"Feature":features,
                        "Importance":clf.feature_importances_}).sort_values("Importance")
    fig10 = px.bar(imp.tail(15), y="Feature", x="Importance", orientation="h",
                   title="Top 15 Feature Importances",
                   color="Importance", color_continuous_scale="Purples")
    fig10.update_layout(**PL, coloraxis_showscale=False, height=420)
    st.plotly_chart(fig10, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 4: PREDICT ───────────────────────────
with tab4:
    st.markdown('<div class="sec-hdr">🧬 Interactive Prediction — Adjust Voice Features</div>',
                unsafe_allow_html=True)
    st.info("Use the sliders to simulate a voice recording and get a real-time Parkinson's prediction from the trained Random Forest model.")

    defaults = df[features].mean().to_dict()
    mins     = df[features].min().to_dict()
    maxs     = df[features].max().to_dict()

    input_vals = {}
    groups = [
        ("🎵 Fundamental Frequency", FREQ_COLS),
        ("〰️ Jitter Features",        JITTER_COLS),
        ("📶 Shimmer Features",        SHIMMER_COLS),
        ("📡 Noise Ratios",            RATIO_COLS),
        ("🌀 Nonlinear Dynamics",      NONLINEAR_COLS),
    ]
    for grp_name, grp_cols in groups:
        st.markdown(f'<div class="sec-hdr">{grp_name}</div>', unsafe_allow_html=True)
        gcols = st.columns(min(3, len(grp_cols)))
        for i, feat in enumerate(grp_cols):
            with gcols[i % len(gcols)]:
                lo   = float(mins[feat])
                hi   = float(maxs[feat])
                dv   = float(defaults[feat])
                step = max((hi-lo)/200, 1e-6)
                input_vals[feat] = st.slider(feat, lo, hi, dv, step=step, format="%.5f")

    if st.button("🔍 Run Prediction", use_container_width=True, type="primary"):
        x_in = np.array([[input_vals[f] for f in features]])
        x_sc = sc.transform(x_in)
        pred = clf.predict(x_sc)[0]
        prob = clf.predict_proba(x_sc)[0]
        conf = round(prob[pred]*100, 1)

        if pred == 1:
            st.markdown(f"""
            <div class="pred-box pred-pos">
              <div class="pred-title">🔴 Parkinson's Detected</div>
              <div class="pred-conf">Confidence: <strong>{conf}%</strong></div>
              <div class="pred-conf" style="margin-top:8px;font-size:.85rem">
                Healthy {round(prob[0]*100,1)}% · Parkinson's {round(prob[1]*100,1)}%
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="pred-box pred-neg">
              <div class="pred-title">🟢 Healthy Voice Pattern</div>
              <div class="pred-conf">Confidence: <strong>{conf}%</strong></div>
              <div class="pred-conf" style="margin-top:8px;font-size:.85rem">
                Healthy {round(prob[0]*100,1)}% · Parkinson's {round(prob[1]*100,1)}%
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig11 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(prob[1]*100, 1),
            title={"text":"Parkinson's Probability (%)"},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"#7c3aed"},
                "steps":[
                    {"range":[0,30],"color":"#dcfce7"},
                    {"range":[30,70],"color":"#fef9c3"},
                    {"range":[70,100],"color":"#fee2e2"},
                ],
                "threshold":{"line":{"color":"#dc2626","width":4},"value":70},
            },
            delta={"reference":50},
        ))
        fig11.update_layout(**PL, height=300)
        st.plotly_chart(fig11, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.caption("⚠️ Educational/research use only. Not a clinical diagnostic tool.")

# ── TAB 5: DATA EXPLORER ─────────────────────
with tab5:
    st.markdown(f"**{len(dff):,}** records match current filters.")
    c1, c2 = st.columns([3,1])
    with c1:
        search = st.text_input("🔍 Filter by patient ID", "")
    with c2:
        n_rows = st.slider("Rows to show", 10, 195, 50)

    disp = dff.copy()
    if search:
        disp = disp[disp["patient_id"].str.contains(search, case=False)]

    show_cols = ["name","label"] + features[:10]
    st.dataframe(disp[show_cols].head(n_rows).reset_index(drop=True),
                 use_container_width=True, height=440)

    st.markdown("**📊 Summary Statistics**")
    st.dataframe(dff[features].describe().T, use_container_width=True)

    st.download_button(
        "⬇️ Download Filtered Data (CSV)",
        data=dff.to_csv(index=False).encode("utf-8"),
        file_name="parkinsons_filtered.csv",
        mime="text/csv",
    )

# ── FOOTER
st.markdown("---")
st.caption("🧠 Parkinson's Voice Analytics · UCI ML Repository · Streamlit + Plotly + Scikit-learn")
