import streamlit as st
import pandas as pd
import numpy as np
import joblib
from scipy.stats import skew, kurtosis
from scipy.fft import rfft, rfftfreq
import os
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
from catboost import CatBoostClassifier
from db_queries import insert_prediction
from db_queries import insert_alert
from datetime import datetime, timedelta
import time


##
st.markdown("""
<style>
    /* hide full default navigation */
    [data-testid="stSidebarNav"] {display: none;}

    /* reduce empty space */
    section[data-testid="stSidebar"] {
        padding-top: 20px;
    }
</style>
""", unsafe_allow_html=True)
##
##
import streamlit as st
from ui.sidebar import render_sidebar

render_sidebar(st.session_state.role)


##

st.markdown("""
<style>

/* FIXED HEADER */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: white;
    border-bottom: 1px solid #e6e6e6;
    z-index: 9999;

    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
}

/* TITLE */
.header-title {
    font-size: 18px;
    font-weight: bold;
    color: #111;
}



</style>
""", unsafe_allow_html=True)



# Clear cache once per session (optional safe reset)
if "cache_cleared" not in st.session_state:
    st.cache_data.clear()
    st.session_state["cache_cleared"] = True


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title=" Fault and Severity Predictor", layout="wide")


# ==========================================================
# SESSION STATE INIT
# ==========================================================
if "results" not in st.session_state:
    st.session_state["results"] = None


# ==========================================================
# CUSTOM THEME
# ==========================================================
st.markdown("""
<style>

/* APP BACKGROUND (LIGHT THEME) */
body {
    background-color: #ffffff;
    color: #111;
}

.stApp {
    background: #ffffff;
    color: #111;
}

/* HEADINGS */
h1, h2, h3, h4 {
    color: #0f172a !important;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 700;
}

/* TEXT */
.stMarkdown {
    color: #222 !important;
    font-size: 16px;
}

/* METRICS */
div[data-testid="stMetricValue"] {
    color: #16a34a !important;
    font-size: 28px;
    font-weight: bold;
}

div[data-testid="stMetricLabel"] {
    color: #334155 !important;
    font-size: 15px;
}

/* BUTTONS (CLEAN BLUE STYLE) */
.stButton>button {
    background: linear-gradient(90deg, #007bff, #00c6ff) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 10px 18px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    width: 100% !important;
    transition: 0.3s;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #0056d2, #0096ff) !important;
    transform: scale(1.02);
}

/* TEXT INPUT */
.stTextInput>div>div>input {
    background-color: #ffffff !important;
    color: #111 !important;
    border-radius: 10px !important;
    border: 1px solid #d1d5db !important;
}

/* FILE UPLOADER */
.stFileUploader {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
    padding: 15px !important;
}

/* DATAFRAME */
.stDataFrame {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* LAYOUT */
.block-container {
    padding-top: 1.5rem;
}

/* FILE UPLOADER BUTTON */
div[data-testid="stFileUploader"] button {
    background: linear-gradient(90deg, #007bff, #00c6ff) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: bold !important;
    padding: 10px 18px !important;
    font-size: 16px !important;
}

div[data-testid="stFileUploader"] button:hover {
    background: linear-gradient(90deg, #0056d2, #0096ff) !important;
}

/* UPLOADER TEXT */
div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] span {
    color: #111 !important;
}

/* DOWNLOAD BUTTON */
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(90deg, #007bff, #00c6ff) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: bold !important;
    padding: 10px 18px !important;
    font-size: 16px !important;
    width: 100% !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(90deg, #0056d2, #0096ff) !important;
}

/* SELECTBOX LABELS */
div[data-testid="stSelectbox"] label {
    color: #111 !important;
    font-weight: bold !important;
}

/* HOME PAGE CARDS */
.home-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 5px 5px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    height: 100%;
    transition: box-shadow 0.2s, transform 0.2s;
}
.home-card:hover {
    box-shadow: 0 6px 24px rgba(0,123,255,0.13);
    transform: translateY(-3px);
}
.home-card-icon {
    font-size: 36px;
    margin-bottom: 12px;
}
.home-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 10px;
}
.home-card-text {
    font-size: 14px;
    color: #475569;
    line-height: 1.7;
}


/* LIVE BADGE */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #eaffea;
    border: 1.5px solid #39ff14;
    border-radius: 25px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 700;
    color: #1a7f1a;
    margin-left: 15px;
}

/* blinking dot */
.live-dot {
    width: 10px;
    height: 10px;
    background: #39ff14;
    border-radius: 50%;
    animation: blink 1s infinite;
}

@keyframes blink {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.2; transform: scale(0.6); }
    100% { opacity: 1; transform: scale(1); }
}

/* date style */
.live-date {
    font-size: 12px;
    color: #555;
    margin-left: 10px;
    font-weight: 500;
}

@keyframes livepulse {
    0%   { opacity: 1; transform: scale(1); }
    50%  { opacity: 0.25; transform: scale(0.7); }
    100% { opacity: 1; transform: scale(1); }
}
#
            /* ── page header ── */
.pg-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1.25rem; margin-bottom: 1.5rem;
    border-bottom: 1px solid #E2E6EE; flex-wrap: wrap; gap: 10px;
}
.pg-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.55rem; font-weight: 800; color: #0F1623;
    display: flex; align-items: center; gap: 10px;
}
            .header-datetime {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #111827;
    background: #F8FAFC;
    border: 1px solid #E2E6EE;
    padding: 6px 10px;
    border-radius: 10px;
}

.live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 700; letter-spacing: .04em;
    color: #166534; background: #F0FDF4;
    border: 1px solid #BBF7D0; padding: 4px 12px; border-radius: 99px;
    cursor: default;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #22C55E; animation: lp 2s infinite;
}
@keyframes lp { 0%,100%{opacity:1;} 50%{opacity:.2;} }

          
</style>
            
""", unsafe_allow_html=True)




# ==========================================================
# TITLE  (Updated: Fault and Severity Predictor + LIVE badge)
# ==========================================================
now_txt = datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">
        ⚠️ Fault and Severity Predictor
        <span class="live-pill"><span class="live-dot"></span>Live</span>
        <span class="header-datetime">{now_txt}</span>
    </div>
    
  </div>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# LOAD MODELS
# ==========================================================
MODEL_TYPE_PATH = "model_type.pkl"
MODEL_SEV_PATH = "model_severity.pkl"
LE_TYPE_PATH = "le_type.pkl"
LE_SEV_PATH = "le_sev.pkl"

cat_type = None
cat_sev = None
le_type = None
le_sev = None

if os.path.exists(MODEL_TYPE_PATH) and os.path.exists(MODEL_SEV_PATH):
    cat_type = joblib.load(MODEL_TYPE_PATH)
    cat_sev = joblib.load(MODEL_SEV_PATH)
    le_type = joblib.load(LE_TYPE_PATH)
    le_sev = joblib.load(LE_SEV_PATH)
    st.success("✅ Models loaded successfully!")
else:
    st.warning("⚠️ No trained models found. Please train a model first.")

# ==========================================================
# STORE MODELS IN SESSION STATE
# ==========================================================
if cat_type is not None:
    st.session_state["cat_type"] = cat_type
    st.session_state["cat_sev"] = cat_sev
    st.session_state["le_type"] = le_type
    st.session_state["le_sev"] = le_sev

# ==========================================================


# HELPER FUNCTIONS
# ==========================================================
def split_signal(signal, window_size=2048, overlap=0.5):
    step = int(window_size * (1 - overlap))
    return [signal[i:i + window_size] for i in range(0, len(signal) - window_size + 1, step)]


def extract_features(signal, fs=10000):
    signal = np.array(signal, dtype=np.float32)

    if len(signal) < 2:
        signal = np.pad(signal, (0, 2 - len(signal)), mode="constant")

    features = []
    features.append(np.mean(signal))
    features.append(np.std(signal))
    features.append(np.max(signal))
    features.append(np.min(signal))
    features.append(np.sqrt(np.mean(signal ** 2)))
    features.append(skew(signal))
    features.append(kurtosis(signal))
    features.append(np.max(signal) - np.min(signal))
    features.append(np.max(np.abs(signal)) / (np.sqrt(np.mean(signal ** 2)) + 1e-10))

    fft_vals = np.abs(rfft(signal))
    freqs = rfftfreq(len(signal), 1 / fs)

    features.append(np.mean(fft_vals))
    features.append(np.std(fft_vals))
    features.append(freqs[np.argmax(fft_vals)])
    features.append(np.sum(fft_vals ** 2))
    features.append(np.sum(fft_vals[:10] ** 2))
    features.append(np.sum(fft_vals[-10:] ** 2))

    diff_sig = np.diff(signal)
    if len(diff_sig) == 0:
        diff_sig = np.array([0], dtype=np.float32)

    features.append(np.sum(diff_sig ** 2))
    features.append(np.percentile(signal, 25))
    features.append(np.percentile(signal, 50))
    features.append(np.percentile(signal, 75))

    features.append(np.median(diff_sig))
    features.append(np.mean(diff_sig))
    features.append(np.std(diff_sig))
    features.append(np.max(diff_sig))
    features.append(np.min(diff_sig))

    features.append(np.max(diff_sig) / (np.sqrt(np.mean(diff_sig ** 2)) + 1e-10))

    features.append(np.mean(np.abs(signal)))
    features.append(np.mean(np.abs(diff_sig)))
    features.append(np.sum(np.abs(diff_sig)))
    features.append(np.max(np.abs(diff_sig)))

    features.append(np.sum(signal ** 2))
    features.append(np.sqrt(np.mean(signal ** 2)))
    features.append(np.var(signal))
    features.append(np.std(diff_sig))

    return features


def get_labels_from_filename(filename):
    fname = filename.upper()

    if "H_" in fname or fname.startswith("H_"):
        return "H", "Normal"

    if "_B_" in fname or fname.startswith("B_"):
        fault_type = "B"
    elif "_C_" in fname or fname.startswith("C_"):
        fault_type = "C"
    elif "_I_" in fname or fname.startswith("I_"):
        fault_type = "I"
    elif "_O_" in fname or fname.startswith("O_"):
        fault_type = "O"
    else:
        fault_type = None

    if "0.5X" in fname:
        severity = "Medium"
    else:
        severity = "Severe"

    return fault_type, severity


def read_signals(uploaded_file, skiprows=22):
    try:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, skiprows=skiprows, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded_file, skiprows=skiprows, sep=None, engine="python")
    except:
        return None

    if df.shape[1] < 4:
        return None

    x_sig = df.iloc[:, 1].to_numpy(dtype=np.float32)
    y_sig = df.iloc[:, 2].to_numpy(dtype=np.float32)
    z_sig = df.iloc[:, 3].to_numpy(dtype=np.float32)

    return x_sig, y_sig, z_sig


def read_signals_from_path(filepath, skiprows=22):
    try:
        if filepath.endswith(".xlsx"):
            df = pd.read_excel(filepath, skiprows=skiprows, engine="openpyxl")
        else:
            df = pd.read_csv(filepath, skiprows=skiprows, sep=None, engine="python")
    except:
        return None

    if df.shape[1] < 4:
        return None

    x_sig = df.iloc[:, 1].to_numpy(dtype=np.float32)
    y_sig = df.iloc[:, 2].to_numpy(dtype=np.float32)
    z_sig = df.iloc[:, 3].to_numpy(dtype=np.float32)

    return x_sig, y_sig, z_sig


# ==========================================================
# TABS
# ==========================================================
tab_home, tab_test, tab_pred, tab_train = st.tabs(["💡 Home", "🔍Testing", "🎯 Prediction", "🔄 Train New Model"])

# ==========================================================
# TAB HOME  (Cards Layout)
# ==========================================================
with tab_home:
 

    # Row 1: 3 cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">⚙️</div>
            <div class="home-card-title">How It Works</div>
            <div class="home-card-text">
                Vibration signals are collected from three axes: <b>X, Y, Z</b>.
                Each signal is split into overlapping windows for detailed analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🔬</div>
            <div class="home-card-title">Feature Extraction</div>
            <div class="home-card-text">
                Features are extracted in both <b>time-domain</b> and <b>frequency-domain</b>
                (RMS, skewness, kurtosis, FFT energy, peak frequency, and more).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🎯</div>
            <div class="home-card-title">AI Prediction</div>
            <div class="home-card-text">
                A <b>CatBoost</b> classifier predicts the <b>Fault Type</b> and <b>Fault Severity</b>
                with a confidence score for each window.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: 3 cards
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">📤</div>
            <div class="home-card-title">Output</div>
            <div class="home-card-text">
                • <b>Fault Type</b> → B, C, H, I, O<br>
                • <b>Fault Severity</b> → Normal, Medium, Severe<br>
                • <b>Confidence Score</b> → 0 to 100%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🔍</div>
            <div class="home-card-title">Testing Tab</div>
            <div class="home-card-text">
                Evaluate model performance using <b>labeled vibration datasets</b>.
                View accuracy, classification report, and confusion matrix.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🔄</div>
            <div class="home-card-title">Train New Model</div>
            <div class="home-card-text">
                Retrain the model using a <b>new dataset folder</b> on your machine.
                Supports SMOTE oversampling and custom CatBoost iterations.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# TAB 1: TESTING
# ==========================================================
with tab_test:
    st.subheader(" Testing the Model")

    test_files = st.file_uploader(
        "Upload labeled test files (CSV/XLS/XLSX)",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=True,
        key="test_uploader"
    )

    if test_files and "cat_type" in st.session_state:

        if st.button(" Run Testing Evaluation"):
            y_true_type = []
            y_pred_type = []

            y_true_sev = []
            y_pred_sev = []

            with st.spinner("Testing model performance... Please wait."):

                for file in test_files:
                    true_type, true_sev = get_labels_from_filename(file.name)

                    if true_type is None:
                        continue

                    signals = read_signals(file)
                    if signals is None:
                        continue

                    x_sig, y_sig, z_sig = signals

                    x_sig /= np.max(np.abs(x_sig)) + 1e-10
                    y_sig /= np.max(np.abs(y_sig)) + 1e-10
                    z_sig /= np.max(np.abs(z_sig)) + 1e-10

                    x_win = split_signal(x_sig)
                    y_win = split_signal(y_sig)
                    z_win = split_signal(z_sig)

                    X_windows = np.array([
                        extract_features(wx) + extract_features(wy) + extract_features(wz)
                        for wx, wy, wz in zip(x_win, y_win, z_win)
                    ])

                    pred_type = st.session_state["cat_type"].predict(X_windows)
                    pred_sev = st.session_state["cat_sev"].predict(X_windows)

                    pred_type_label = st.session_state["le_type"].inverse_transform(pred_type)
                    pred_sev_label = st.session_state["le_sev"].inverse_transform(pred_sev)

                    final_pred_type = pd.Series(pred_type_label).mode()[0]
                    final_pred_sev = pd.Series(pred_sev_label).mode()[0]

                    y_true_type.append(true_type)
                    y_pred_type.append(final_pred_type)

                    y_true_sev.append(true_sev)
                    y_pred_sev.append(final_pred_sev)

            if len(y_true_type) == 0:
                st.error("❌ No valid labeled test files were detected.")
            else:
                acc_type = accuracy_score(y_true_type, y_pred_type)
                acc_sev = accuracy_score(y_true_sev, y_pred_sev)

                st.success("✅ Testing Completed Successfully!")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Fault Type Accuracy", f"{acc_type*100:.2f}%")
                with col2:
                    st.metric("Fault Severity Accuracy", f"{acc_sev*100:.2f}%")

                st.subheader("📌 Classification Report (Fault Type)")
                st.text(classification_report(y_true_type, y_pred_type))

                st.subheader("📌 Confusion Matrix (Fault Type)")
                st.dataframe(confusion_matrix(y_true_type, y_pred_type))

                st.subheader("📌 Classification Report (Fault Severity)")
                st.text(classification_report(y_true_sev, y_pred_sev))

                st.subheader("📌 Confusion Matrix (Fault Severity)")
                st.dataframe(confusion_matrix(y_true_sev, y_pred_sev))

# ==========================================================
# TAB 2: PREDICTION
# ==========================================================
with tab_pred:
    st.subheader(" Predict Fault Type and Severity")

    uploaded_files = st.file_uploader(
        "Upload signal files (CSV/XLS/XLSX)",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=True,
        key="predict_uploader"
    )

    if uploaded_files and "cat_type" in st.session_state:
        if st.button("Predict All Files"):

            all_results = []

            with st.spinner("Predicting... Please wait."):
                for file in uploaded_files:

                    signals = read_signals(file)
                    if signals is None:
                        continue

                    x_sig, y_sig, z_sig = signals
                    x_sig /= np.max(np.abs(x_sig)) + 1e-10
                    y_sig /= np.max(np.abs(y_sig)) + 1e-10
                    z_sig /= np.max(np.abs(z_sig)) + 1e-10

                    x_win = split_signal(x_sig)
                    y_win = split_signal(y_sig)
                    z_win = split_signal(z_sig)

                    X_windows = np.array([
                        extract_features(wx) + extract_features(wy) + extract_features(wz)
                        for wx, wy, wz in zip(x_win, y_win, z_win)
                    ])

                    type_pred = st.session_state["cat_type"].predict(X_windows)
                    type_conf = np.max(st.session_state["cat_type"].predict_proba(X_windows), axis=1)

                    sev_pred = st.session_state["cat_sev"].predict(X_windows)
                    sev_conf = np.max(st.session_state["cat_sev"].predict_proba(X_windows), axis=1)

                    type_labels = st.session_state["le_type"].inverse_transform(type_pred)
                    sev_labels = st.session_state["le_sev"].inverse_transform(sev_pred)

                    # ==========================================================
                    # ✅ INSERT ALERTS (1 second delay between each row)
                    # ==========================================================
                    fault_map = {
                        "I": "Inner race fault",
                        "O": "Outer race fault",
                        "B": "Ball fault",
                        "C": "Combination fault",
                    }
                    base_time = datetime.now()
                    for i in range(len(sev_labels)):
                        alert_time = base_time + timedelta(seconds=i)
                        fault_name = fault_map.get(type_labels[i], "Unknown Fault")

                        if sev_labels[i].lower() == "severe":
                            insert_alert(
                                machine_id=42,
                                timestamp=alert_time.strftime("%Y-%m-%d %H:%M:%S"),
                                alert_type="Critical Alert",
                                message=f"Machine is in extremely dangerous condition ",
                                fault_type=fault_name,
                                severity="severe",
                                is_anomaly=0,
                                status="active"
                            )
                            time.sleep(1)

                        elif sev_labels[i].lower() == "medium":
                            insert_alert(
                                machine_id=42,
                                timestamp=alert_time.strftime("%Y-%m-%d %H:%M:%S"),
                                alert_type="Warning",
                                message=f"Machine is in moderately dangerous condition ",
                                fault_type=fault_name,
                                severity="medium",
                                is_anomaly=0,
                                status="active"
                            )
                            time.sleep(1)

                    # ==========================================================
                    # ✅ INSERT PREDICTIONS (timestamp +1 second)
                    # ==========================================================
                    base_time = datetime.now()

                    for i in range(len(type_labels)):
                        pred_time = base_time + timedelta(seconds=i)
                        insert_prediction(
                            machine_id=42,
                            window_number=i+1,
                            timestamp=pred_time.strftime("%Y-%m-%d %H:%M:%S"),
                            fault_type=type_labels[i],
                            severity=sev_labels[i],
                            type_confidence=float(type_conf[i] * 100),
                            severity_confidence=float(sev_conf[i] * 100),
                        )

                    # ==========================================================
                    # ✅ DISPLAY RESULTS
                    # ==========================================================
                    df_res = pd.DataFrame({
                        "File": file.name,
                        "Window": np.arange(1, len(X_windows) + 1),
                        "Fault Type": type_labels,
                        "Type Confidence": np.round(type_conf * 100, 2),
                        "Fault Severity": sev_labels,
                        "Severity Confidence": np.round(sev_conf * 100, 2)
                    })

                    all_results.append(df_res)

            if all_results:
                final_df = pd.concat(all_results, ignore_index=True)
                st.success("✅ Prediction completed successfully!")
                st.dataframe(final_df, use_container_width=True)
                st.session_state["results"] = final_df

                st.download_button(
                    "⬇️ Download Predictions CSV",
                    final_df.to_csv(index=False),
                    "predictions.csv",
                    mime="text/csv"
                )

# MODEL CONFIDENCE OVERVIEW
# ==========================================================

    if "results" in st.session_state and st.session_state["results"] is not None:

        df = st.session_state["results"]

        if not df.empty:
            st.subheader("📊 Model Confidence Overview")

        severity_colors = {
            "Severe": "#FF8C00",
            "Medium": "#FFD700",
            "Normal": "#00FF7F"
        }

        type_colors = {
            "B": "#00BFFF",
            "C": "#FF1493",
            "H": "#39ff14",
            "I": "#9400D3",
            "O": "#8400FF"
        }

        type_conf_avg = df.groupby("Fault Type")["Type Confidence"].mean().reset_index()
        sev_conf_avg = df.groupby("Fault Severity")["Severity Confidence"].mean().reset_index()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Fault Type Confidence")
            fig_type = px.bar(
                type_conf_avg,
                x="Fault Type",
                y="Type Confidence",
                text="Type Confidence",
                color="Fault Type",
                color_discrete_map=type_colors,
                title="Average Confidence per Fault Type (%)"
            )
            fig_type.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig_type.update_layout(
                yaxis=dict(range=[0, 100]),
                showlegend=True,
                legend_title="Fault Type"
            )
            st.plotly_chart(fig_type, use_container_width=True)

        with col2:
            st.markdown("### Fault Severity Confidence")
            fig_sev = px.bar(
                sev_conf_avg,
                x="Fault Severity",
                y="Severity Confidence",
                text="Severity Confidence",
                color="Fault Severity",
                color_discrete_map=severity_colors,
                title="Average Confidence per Severity Level (%)"
            )
            fig_sev.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig_sev.update_layout(
                yaxis=dict(range=[0, 100]),
                showlegend=True,
                legend_title="Severity Level"
            )
            st.plotly_chart(fig_sev, use_container_width=True)


# ==========================================================
# FILTER RESULTS
# ==========================================================

    if "results" in st.session_state and st.session_state["results"] is not None and not st.session_state["results"].empty:

        st.subheader("🔍 Filter Results")

        df = st.session_state["results"]

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_file = st.selectbox(
                "Filter by File",
                ["All"] + list(df["File"].unique())
            )

        with col2:
            selected_type = st.selectbox(
                "Filter by Fault Type",
                ["All"] + list(df["Fault Type"].unique())
            )

        with col3:
            selected_severity = st.selectbox(
                "Filter by Fault Severity",
                ["All"] + list(df["Fault Severity"].unique())
            )

        filtered_df = df.copy()

        if selected_file != "All":
            filtered_df = filtered_df[filtered_df["File"] == selected_file]

        if selected_type != "All":
            filtered_df = filtered_df[filtered_df["Fault Type"] == selected_type]

        if selected_severity != "All":
            filtered_df = filtered_df[filtered_df["Fault Severity"] == selected_severity]

        st.dataframe(filtered_df, use_container_width=True)


# ==========================================================
# TAB 3: TRAIN NEW MODEL
# ==========================================================
with tab_train:
    st.subheader("Train New Model From Local Dataset Folder")

    st.markdown("""
This mode trains the model **without uploading any file**.

📌 Enter the folder path where your dataset files are stored.
Example:
`E:\\SmartGridSystem\\raw_data`
""")

    dataset_path = st.text_input("Dataset Folder Path", value="E:\\SmartGridSystem\\raw_data")

    iterations = st.slider("CatBoost Iterations", 100, 2000, 500, step=100)
    test_size = st.slider("Test Size (%)", 10, 40, 20, step=5)

    use_smote = st.checkbox("Use SMOTE Oversampling", value=True)

    if st.button(" Train New Models Now"):

        if not os.path.exists(dataset_path):
            st.error("❌ Folder path not found. Please enter a valid path.")
        else:
            all_files = []
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.endswith((".csv", ".xls", ".xlsx")):
                        all_files.append(os.path.join(root, file))

            st.success(f"✅ Found {len(all_files)} files in dataset folder.")

            if len(all_files) == 0:
                st.error("❌ No valid dataset files found.")
            else:
                X = []
                y_type = []
                y_sev = []

                with st.spinner("Extracting features from dataset... Please wait."):

                    for filepath in all_files:
                        filename = os.path.basename(filepath)

                        fault_type, severity = get_labels_from_filename(filename)
                        if fault_type is None:
                            continue

                        signals = read_signals_from_path(filepath)
                        if signals is None:
                            continue

                        x_sig, y_sig, z_sig = signals

                        x_sig /= np.max(np.abs(x_sig)) + 1e-10
                        y_sig /= np.max(np.abs(y_sig)) + 1e-10
                        z_sig /= np.max(np.abs(z_sig)) + 1e-10

                        x_win = split_signal(x_sig)
                        y_win = split_signal(y_sig)
                        z_win = split_signal(z_sig)

                        for wx, wy, wz in zip(x_win, y_win, z_win):
                            feats = extract_features(wx) + extract_features(wy) + extract_features(wz)
                            X.append(feats)
                            y_type.append(fault_type)
                            y_sev.append(severity)

                X = np.array(X)
                y_type = np.array(y_type)
                y_sev = np.array(y_sev)

                st.success("✅ Feature extraction completed!")
                st.info(f"Samples: {X.shape[0]} | Features: {X.shape[1]}")

                le_type_new = LabelEncoder()
                y_type_enc = le_type_new.fit_transform(y_type)

                le_sev_new = LabelEncoder()
                y_sev_enc = le_sev_new.fit_transform(y_sev)

                # Train Fault Type Model
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_type_enc, test_size=test_size / 100, random_state=42, stratify=y_type_enc
                )

                if use_smote:
                    try:
                        sm = SMOTE(random_state=42)
                        X_train, y_train = sm.fit_resample(X_train, y_train)
                        st.success("✅ SMOTE applied (Fault Type)")
                    except:
                        st.warning("⚠️ SMOTE failed (Fault Type). Training without oversampling.")

                model_type_new = CatBoostClassifier(
                    iterations=iterations,
                    depth=10,
                    learning_rate=0.05,
                    loss_function="MultiClass",
                    random_seed=42,
                    verbose=100
                )

                with st.spinner("Training Fault Type model..."):
                    model_type_new.fit(X_train, y_train)

                y_pred = model_type_new.predict(X_test)
                acc_type = accuracy_score(y_test, y_pred)

                st.subheader("📌 Fault Type Training Results")
                st.metric("Accuracy (Fault Type)", f"{acc_type * 100:.2f}%")
                st.text(classification_report(y_test, y_pred, target_names=le_type_new.classes_))
                st.dataframe(confusion_matrix(y_test, y_pred))

                # Train Severity Model
                X_train2, X_test2, y_train2, y_test2 = train_test_split(
                    X, y_sev_enc, test_size=test_size / 100, random_state=42, stratify=y_sev_enc
                )

                if use_smote:
                    try:
                        sm2 = SMOTE(random_state=42)
                        X_train2, y_train2 = sm2.fit_resample(X_train2, y_train2)
                        st.success("✅ SMOTE applied (Severity)")
                    except:
                        st.warning("⚠️ SMOTE failed (Severity). Training without oversampling.")

                model_sev_new = CatBoostClassifier(
                    iterations=iterations,
                    depth=10,
                    learning_rate=0.05,
                    loss_function="MultiClass",
                    random_seed=42,
                    verbose=100
                )

                with st.spinner("Training Severity model..."):
                    model_sev_new.fit(X_train2, y_train2)

                y_pred2 = model_sev_new.predict(X_test2)
                acc_sev = accuracy_score(y_test2, y_pred2)

                st.subheader("📌 Severity Training Results")
                st.metric("Accuracy (Severity)", f"{acc_sev * 100:.2f}%")
                st.text(classification_report(y_test2, y_pred2, target_names=le_sev_new.classes_))
                st.dataframe(confusion_matrix(y_test2, y_pred2))

                # Save models
                joblib.dump(model_type_new, "model_type.pkl")
                joblib.dump(model_sev_new, "model_severity.pkl")
                joblib.dump(le_type_new, "le_type.pkl")
                joblib.dump(le_sev_new, "le_sev.pkl")

                st.success("✅ Models saved successfully!")

                # Reload models automatically
                st.session_state["cat_type"] = joblib.load("model_type.pkl")
                st.session_state["cat_sev"] = joblib.load("model_severity.pkl")
                st.session_state["le_type"] = joblib.load("le_type.pkl")
                st.session_state["le_sev"] = joblib.load("le_sev.pkl")

                st.success("🔄 Models reloaded! You can now go to Prediction tab and use the new models.")