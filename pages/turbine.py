"""
Autoencoder Anomaly Detection - Production Application
Cyber/Hacker Theme with Horizontal Underline Navigation
Manual execution buttons for Testing, Prediction, and Training
"""

import os
import warnings
import numpy as np
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    precision_recall_curve, average_precision_score, roc_auc_score
)
import tensorflow as tf
from keras.models import load_model, Model
from keras.layers import Input, Dense
from keras.callbacks import EarlyStopping

warnings.filterwarnings('ignore')
from db_queries import insert_anomaly
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


/* HOME PAGE CARDS */
.home-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 4px 4px;
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

</style>
""", unsafe_allow_html=True)






# Clear cache once per session (optional safe reset)
if "cache_cleared" not in st.session_state:
    st.cache_data.clear()
    st.session_state["cache_cleared"] = True






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
    body {
        background-color: #000000;
        color: white;
    }
    .stApp {
        background: linear-gradient(to bottom right, #000000, #001a00);
        color: white;
    }
    h1, h2, h3, h4 {
        color: #39ff14 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .stMarkdown {
        color: white;
        font-size: 16px;
    }
    div[data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-size: 28px;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        color: white !important;
        font-size: 15px;
    }
    .stButton>button {
        background-color: #39ff14 !important;
        color: black !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 18px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        background-color: #2ecc0f !important;
        color: black !important;
        border: none !important;
    }
    .stTextInput>div>div>input {
        background-color: #111111 !important;
        color: #39ff14 !important;
        border-radius: 10px !important;
        border: 1px solid #39ff14 !important;
    }
    .stFileUploader {
        background-color: #111111 !important;
        border: 1px solid #39ff14 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    .stDataFrame {
        border: 1px solid #39ff14 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    .block-container {
        padding-top: 80rem;
    }

     /* APP BACKGROUND (LIGHT THEME) */
body {
    background-color: #ffffff;
    color: #111;
}

.stApp {
    background: white;
    color:white;
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
/* ── page header ── */
.pg-header {
    border-bottom: none !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
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




# =============================================================================
# Configuration
# =============================================================================
MODEL_DIR = "anomaly_detector_model"
MODEL_PATH = os.path.join(MODEL_DIR, "autoencoder_final.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_columns.pkl")
THRESHOLD_PATH = os.path.join(MODEL_DIR, "threshold.pkl")

# =============================================================================
# Helper Functions
# =============================================================================
def load_model_artifacts():
    try:
        model = load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        feature_columns = joblib.load(FEATURES_PATH)
        threshold = joblib.load(THRESHOLD_PATH)
        return model, scaler, feature_columns, threshold
    except Exception as e:
        st.error(f"Failed to load model artifacts: {e}")
        st.stop()

def clean_dataframe(df):
    df_clean = df.copy()
    cols_to_clean = ['°C TF', 'ppm SO₂', '% CO₂', '% O₂', 'ppm CO', 
                     'ppm NO', 'ppm NO₂', 'ppm NOx', 'mbar Tir.', '°C TA', 'Facteur dilution']
    for col in cols_to_clean:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.replace('°C', '', regex=False)
            df_clean[col] = df_clean[col].str.replace('ppm', '', regex=False)
            df_clean[col] = df_clean[col].str.replace('%', '', regex=False)
            df_clean[col] = df_clean[col].str.replace('mbar', '', regex=False)
            df_clean[col] = df_clean[col].str.replace('x1', '1', regex=False)
            df_clean[col] = df_clean[col].str.replace('-', '', regex=False)
            df_clean[col] = df_clean[col].str.strip()
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    if 'Date/heure' in df_clean.columns:
        df_clean['Date/heure'] = pd.to_datetime(df_clean['Date/heure'], errors='coerce')
        df_clean['hour'] = df_clean['Date/heure'].dt.hour
        df_clean['hour_sin'] = np.sin(2 * np.pi * df_clean['hour'] / 24.0)
        df_clean['hour_cos'] = np.cos(2 * np.pi * df_clean['hour'] / 24.0)
    else:
        df_clean['hour_sin'] = 0.0
        df_clean['hour_cos'] = 0.0
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isna().all():
            df_clean[col] = 0.0
        else:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
    return df_clean

def preprocess_for_prediction(df_raw, scaler, feature_columns):
    df_clean = clean_dataframe(df_raw)
    missing_cols = [col for col in feature_columns if col not in df_clean.columns]
    if missing_cols:
        st.warning(f"Missing required columns: {missing_cols}. Filling with zeros.")
        for col in missing_cols:
            df_clean[col] = 0.0
    X = df_clean[feature_columns].values
    X = np.nan_to_num(X, nan=0.0)
    X_scaled = scaler.transform(X)
    return X_scaled, df_clean

def predict_anomaly(model, X_scaled, threshold):
    pred = model.predict(X_scaled, verbose=0)
    mse = np.mean(np.power(X_scaled - pred, 2), axis=1)
    is_anomaly = (mse > threshold).astype(int)
    return mse, is_anomaly

def retrain_autoencoder(X_train_scaled, input_dim, epochs=50, batch_size=128, validation_split=0.1):
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(6, activation='relu')(input_layer)
    encoded = Dense(4, activation='relu')(encoded)
    encoded = Dense(2, activation='relu')(encoded)
    decoded = Dense(4, activation='relu')(encoded)
    decoded = Dense(6, activation='relu')(decoded)
    decoded = Dense(input_dim, activation='sigmoid')(decoded)
    autoencoder = Model(inputs=input_layer, outputs=decoded)
    autoencoder.compile(optimizer='adam', loss='mse')
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    history = autoencoder.fit(
        X_train_scaled, X_train_scaled,
        epochs=epochs, batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[early_stop], verbose=0
    )
    return autoencoder, history

def save_updated_artifacts(model, scaler, feature_columns, threshold, model_dir=MODEL_DIR):
    os.makedirs(model_dir, exist_ok=True)
    model.save(os.path.join(model_dir, "autoencoder_final.keras"))
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
    joblib.dump(feature_columns, os.path.join(model_dir, "feature_columns.pkl"))
    joblib.dump(threshold, os.path.join(model_dir, "threshold.pkl"))
    st.success(f"Model artifacts saved to '{model_dir}'")

def process_single_file(uploaded_file, model, scaler, feature_columns, threshold):
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        
        X_scaled, df_clean = preprocess_for_prediction(df_raw, scaler, feature_columns)
        mse, is_anomaly = predict_anomaly(model, X_scaled, threshold)
        
        df_result = df_clean.copy()
        df_result['reconstruction_error'] = mse
        df_result['anomaly'] = is_anomaly
        df_result['prediction'] = df_result['anomaly'].map({0: 'Normal', 1: 'Anomaly'})
        
        return {
            'success': True,
            'filename': uploaded_file.name,
            'df_result': df_result,
            'mse': mse,
            'is_anomaly': is_anomaly,
            'threshold': threshold,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'filename': uploaded_file.name,
            'df_result': None,
            'mse': None,
            'is_anomaly': None,
            'threshold': threshold,
            'error': str(e)
        }

def display_prediction_results(result, file_index):
    st.markdown(f"### 📄 File: {result['filename']}")
    
    if not result['success']:
        st.error(f"Error processing file: {result['error']}")
        return
    
    df_result = result['df_result']
    mse = result['mse']
    is_anomaly = result['is_anomaly']
    threshold = result['threshold']
    
    n_anomalies = is_anomaly.sum()
    n_normal = len(is_anomaly) - n_anomalies
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Samples", len(is_anomaly))
    col2.metric("Normal", n_normal)
    col3.metric("Anomalies", n_anomalies)
    
    # Reconstruction error plot
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        subplot_titles=("Reconstruction Error (All Samples)", "Anomaly Highlight"))
    fig.add_trace(go.Scatter(x=np.arange(len(mse)), y=mse, mode='lines', name='Error',
                             line=dict(color='#39ff14', width=1.5)), row=1, col=1)
    fig.add_hline(y=threshold, line_dash="dash", line_color="red", 
                  annotation_text=f"Threshold = {threshold:.5f}", row=1, col=1)
    anomaly_indices = np.where(is_anomaly == 1)[0]
    if len(anomaly_indices) > 0:
        fig.add_trace(go.Scatter(x=anomaly_indices, y=mse[anomaly_indices], mode='markers',
                                 name='Anomaly', marker=dict(color='red', size=6)), row=2, col=1)
    fig.update_layout(height=600, showlegend=True, template='plotly_dark', 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='white'))
    st.plotly_chart(fig, use_container_width=True, key=f"plot_error_{file_index}")
    
    # Histogram
    fig_hist = go.Figure()
    if n_normal > 0:
        fig_hist.add_trace(go.Histogram(x=mse[is_anomaly==0], name='Normal', opacity=0.7, marker_color='#2E86C1'))
    if n_anomalies > 0:
        fig_hist.add_trace(go.Histogram(x=mse[is_anomaly==1], name='Anomaly', opacity=0.7, marker_color='#E74C3C'))
    fig_hist.add_vline(x=threshold, line_dash="dash", line_color="yellow", 
                       annotation_text=f"Threshold = {threshold:.5f}")
    fig_hist.update_layout(
        barmode='overlay',
        title="Reconstruction Error Distribution",
        xaxis_title="MSE",
        yaxis_title="Count",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    if mse.max() / (mse.min() + 1e-10) > 100:
        fig_hist.update_xaxis(type="log")
    st.plotly_chart(fig_hist, use_container_width=True, key=f"plot_hist_{file_index}")
    
    # Download button
    csv_data = df_result.to_csv(index=False).encode('utf-8')
    st.download_button(f"Download {result['filename']} results", csv_data, 
                       f"{result['filename']}_detection_results.csv", "text/csv",
                       key=f"download_{file_index}")
    

# =============================================================================
# Streamlit App Configuration
# =============================================================================

def require_role(allowed_roles):
    if "role" not in st.session_state or st.session_state.role not in allowed_roles:
        st.error("Access Denied.")
        st.stop()

require_role(["admin","turbine_manager"])

  

now_txt = datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">
       📈 Anomaly Detection
        <span class="live-pill"><span class="live-dot"></span>Live</span>
        <span class="header-datetime">{now_txt}</span>
    </div>
    
  </div>
</div>
""", unsafe_allow_html=True)
# Check if model exists
  
if os.path.exists(MODEL_PATH):
    st.success("✅ Model loaded successfully!")
else:
     st.warning("⚠️ Model not found. Please train the model in Training mode.")



# Check if model exists
tab_home, tab_test, tab_pred, tab_train = st.tabs([
    "💡 Home",
    " 🔍Testing",
    "🎯 Prediction",
    "🔄 Train New Model"
])




# =============================================================================
# Page Content
# =============================================================================
# Home Page
with tab_home:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🤖</div>
            <div class="home-card-title">System Overview</div>
            <div class="home-card-text">
                This application uses an <b>Autoencoder Neural Network</b> to detect anomalies
                in gas turbine sensor measurements.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">⚙️</div>
            <div class="home-card-title">How It Works</div>
            <div class="home-card-text">
                The model learns normal operating behavior by reconstructing sensor patterns. 
                    High reconstruction error 
                    indicates abnormal turbine conditions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">📊</div>
            <div class="home-card-title">Reconstruction Error</div>
            <div class="home-card-text">
                Each sample receives an <b>AE_score</b> (MSE error).
                If the score exceeds the learned threshold, it is classified as an anomaly.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">📤</div>
            <div class="home-card-title">Output</div>
            <div class="home-card-text">
                • <b>AE_score</b> → Reconstruction Error (MSE)<br>
                • <b>AE_anomaly</b> → 0 = Normal, 1 = Anomaly<br>
                • <b>Prediction</b> → Normal / Anomaly
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🔍</div>
            <div class="home-card-title">Testing Tab</div>
            <div class="home-card-text">
                Evaluate the model using labeled datasets.
                The system displays metrics such as <b>Accuracy</b>, <b>ROC-AUC</b>,
                confusion matrix, and classification report.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="home-card">
            <div class="home-card-icon">🔄</div>
            <div class="home-card-title">Training Tab</div>
            <div class="home-card-text">
                Retrain the autoencoder using new <b>normal operating data</b>.
                A new threshold is computed automatically using the <b>95th percentile</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    

# =============================================================================
# Testing Page (Evaluation) - Manual execution
# =============================================================================
with tab_test:
    

    st.markdown("## Testing the Model")
    
    
    with st.spinner("Loading model..."):
        model, scaler, feature_columns, threshold = load_model_artifacts()
    
    uploaded_file = st.file_uploader("Choose labeled test file (CSV/Excel)", type=["csv", "xlsx", "xls"])
    
    # Store uploaded file in session state
    if uploaded_file is not None:
        st.session_state.test_file = uploaded_file
    elif 'test_file' in st.session_state:
        uploaded_file = st.session_state.test_file
    
    # Button to start testing
    if uploaded_file is not None and st.button(" Run Testing", key="run_testing", use_container_width=False):
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            
            if 'label' not in df_raw.columns:
                st.error("Label column 'label' not found. Please ensure your file contains a 'label' column with 0=normal, 1=anomaly.")
                st.stop()
            labels = df_raw['label'].values
            
            X_scaled, df_clean = preprocess_for_prediction(df_raw, scaler, feature_columns)
            mse, is_anomaly = predict_anomaly(model, X_scaled, threshold)
            
            # Metrics
            tn, fp, fn, tp = confusion_matrix(labels, is_anomaly).ravel()
            precision = tp / (tp + fp) if (tp+fp)>0 else 0
            recall = tp / (tp + fn) if (tp+fn)>0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision+recall)>0 else 0
            accuracy = (tp+tn) / (tp+tn+fp+fn)
            roc_auc = roc_auc_score(labels, mse)
            ap = average_precision_score(labels, mse)
            
            st.markdown("### Performance Metrics")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Accuracy", f"{accuracy:.2%}")
            col2.metric("Precision", f"{precision:.2%}")
            col3.metric("Recall", f"{recall:.2%}")
            col4.metric("F1-Score", f"{f1:.2%}")
            col5.metric("ROC-AUC", f"{roc_auc:.3f}")
            col6.metric("Avg Precision", f"{ap:.3f}")
            
            # Confusion Matrix
            st.markdown("### Confusion Matrix")
            fig_cm = px.imshow([[tn, fp], [fn, tp]],
                               labels=dict(x="Predicted", y="True", color="Count"),
                               x=["Normal (0)", "Anomaly (1)"],
                               y=["Normal (0)", "Anomaly (1)"],
                               text_auto=True, color_continuous_scale="Greens")
            fig_cm.update_layout(height=450, width=500, template='plotly_dark',
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_cm, use_container_width=False)
            
            # ROC Curve
            fpr, tpr, _ = roc_curve(labels, mse)
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'ROC (AUC={roc_auc:.3f})',
                                         line=dict(color='#39ff14', width=2)))
            fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                                         line=dict(dash='dash', color='gray')))
            fig_roc.update_layout(title="ROC Curve", xaxis_title="False Positive Rate",
                                  yaxis_title="True Positive Rate", template='plotly_dark',
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='white'))
            st.plotly_chart(fig_roc, use_container_width=True)
            
            # Precision-Recall Curve
            prec, rec, _ = precision_recall_curve(labels, mse)
            fig_pr = go.Figure()
            fig_pr.add_trace(go.Scatter(x=rec, y=prec, mode='lines', name=f'PR (AP={ap:.3f})',
                                        line=dict(color='#39ff14', width=2)))
            fig_pr.update_layout(title="Precision-Recall Curve", xaxis_title="Recall",
                                 yaxis_title="Precision", template='plotly_dark',
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white'))
            st.plotly_chart(fig_pr, use_container_width=True)
            
            # Error Distribution
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(x=mse[labels==0], name='Normal', opacity=0.7, marker_color='#2E86C1'))
            fig_dist.add_trace(go.Histogram(x=mse[labels==1], name='Anomaly', opacity=0.7, marker_color='#E74C3C'))
            fig_dist.add_vline(x=threshold, line_dash="dash", line_color="yellow",
                               annotation_text=f"Threshold = {threshold:.5f}")
            fig_dist.update_layout(barmode='overlay', title="Reconstruction Error by True Class",
                                   xaxis_title="MSE", yaxis_title="Count", template='plotly_dark',
                                   paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   font=dict(color='white'))
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Classification Report
            st.markdown("### Classification Report")
            report = classification_report(labels, is_anomaly, target_names=['Normal (0)', 'Anomaly (1)'], output_dict=True)
            report_df = pd.DataFrame(report).transpose()
            st.dataframe(report_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Evaluation failed: {e}")
            st.exception(e)
    elif uploaded_file is not None:
        st.info("Click 'Run Testing' to start evaluation.")
    else:
        st.info("Please upload a labeled test file.")

# =============================================================================
# Prediction Page - Manual execution
# =============================================================================
from datetime import datetime, timedelta

with tab_pred:
    results = []

    st.markdown("## Anomaly Detection ")
    st.markdown("Upload one or more datasets (CSV or Excel) to detect anomalies using the trained autoencoder.")

    with st.spinner("Loading model..."):
        model, scaler, feature_columns, threshold = load_model_artifacts()

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state.prediction_files = uploaded_files
    elif "prediction_files" in st.session_state:
        uploaded_files = st.session_state.prediction_files

    if uploaded_files and len(uploaded_files) > 0 and st.button(" Run Prediction", key="run_prediction"):

        results = []
        progress_bar = st.progress(0)

        for i, file in enumerate(uploaded_files):

            result = process_single_file(file, model, scaler, feature_columns, threshold)
            results.append(result)

            if result.get("success", False):

                mse = result["mse"]
                is_anomaly = result["is_anomaly"]

                # ==========================================================
                # SAVE ANOMALIES (REAL TIME) + DELAY ONLY IF ANOMALY
                # ==========================================================
                for j in range(len(is_anomaly)):

                    if int(is_anomaly[j]) == 1:
                        anomaly_time = datetime.now()

                        insert_anomaly(
                            machine_id=42,
                            timestamp=anomaly_time.strftime("%Y-%m-%d %H:%M:%S"),
                            anomaly_score=float(mse[j]),
                            is_anomaly=int(is_anomaly[j]),
                        )

                        time.sleep(1) 

                # ==========================================================
                # SAVE ALERTS (ONLY FIRST + LAST ANOMALY)
                # ==========================================================
                anomaly_indices = np.where(is_anomaly == 1)[0]

                if len(anomaly_indices) > 0:

                    start_index = int(anomaly_indices[0])
                    end_index = int(anomaly_indices[-1])

                    # Start alert
                    start_alert_time = datetime.now()
                    insert_alert(
                        machine_id=42,
                        timestamp=start_alert_time.strftime("%Y-%m-%d %H:%M:%S"),
                        alert_type="Critical gas emission anomaly detected",
                        message=f"Anomaly started ",
                        fault_type=None,
                        severity=None,
                        is_anomaly=1,
                        status="active"
                    )

                    time.sleep(1)  

                    # End alert
                    end_alert_time = datetime.now()
                    insert_alert(
                        machine_id=42,
                        timestamp=end_alert_time.strftime("%Y-%m-%d %H:%M:%S"),
                        alert_type="Critical gas emission anomaly detected",
                        message=f"Anomaly ended ",
                        fault_type=None,
                        severity=None,
                        is_anomaly=1,
                        status="active"
                    )

            progress_bar.progress((i + 1) / len(uploaded_files))

        progress_bar.empty()
        st.success("✅ Prediction completed!")

        # ==============================
        # RESULTS DISPLAY
        # ==============================
        for idx, result in enumerate(results):
            display_prediction_results(result, idx)

        # ==============================
        # DOWNLOAD COMBINED RESULTS
        # ==============================
        if len(results) > 0 and all(r.get("success", False) for r in results):

            combined_df = pd.concat([r["df_result"] for r in results], ignore_index=True)
            csv_combined = combined_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 Download All Results (Combined)",
                csv_combined,
                "all_detection_results.csv",
                "text/csv"
            )

# =============================================================================
# Training Page - Manual execution
# =============================================================================
with tab_train:
    
    st.markdown("## Model Retraining From Local Dataset Folder")
    st.markdown("Upload a new training dataset (normal data only) to retrain the autoencoder.")
    uploaded_file = st.file_uploader("Upload training data (CSV/Excel) - should contain normal operating data", type=["csv", "xlsx", "xls"])
    
    # Store uploaded file in session state
    if uploaded_file is not None:
        st.session_state.train_file = uploaded_file
    elif 'train_file' in st.session_state:
        uploaded_file = st.session_state.train_file
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_train_raw = pd.read_csv(uploaded_file)
            else:
                df_train_raw = pd.read_excel(uploaded_file)
            st.markdown("### Training Data Preview")
            st.dataframe(df_train_raw.head(10), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                epochs = st.number_input("Epochs", min_value=10, max_value=200, value=50, step=10)
            with col2:
                batch_size = st.selectbox("Batch Size", [32, 64, 128, 256], index=2)
            
            _, scaler, feature_columns, _ = load_model_artifacts()
            
            if st.button(" Run Training", key="run_training", use_container_width=False):
                with st.spinner("Preprocessing training data..."):
                    df_clean = clean_dataframe(df_train_raw)
                    for col in feature_columns:
                        if col not in df_clean.columns:
                            df_clean[col] = 0.0
                    X_train = df_clean[feature_columns].values
                    X_train = np.nan_to_num(X_train, nan=0.0)
                    X_train_scaled = scaler.transform(X_train)
                
                with st.spinner("Training autoencoder..."):
                    input_dim = X_train_scaled.shape[1]
                    model, history = retrain_autoencoder(X_train_scaled, input_dim, epochs=epochs, batch_size=batch_size, validation_split=0.1)
                
                train_pred = model.predict(X_train_scaled, verbose=0)
                train_mse = np.mean(np.power(X_train_scaled - train_pred, 2), axis=1)
                new_threshold = np.quantile(train_mse, 0.95)
                
                st.markdown("### Training History")
                fig_loss = go.Figure()
                fig_loss.add_trace(go.Scatter(y=history.history['loss'], mode='lines', name='Training Loss', line=dict(color='#39ff14')))
                fig_loss.add_trace(go.Scatter(y=history.history['val_loss'], mode='lines', name='Validation Loss', line=dict(color='orange')))
                fig_loss.update_layout(title="Loss Curves", xaxis_title="Epoch", yaxis_title="MSE", template='plotly_dark',
                                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                       font=dict(color='white'))
                st.plotly_chart(fig_loss, use_container_width=True)
                st.success(f"Training completed. New threshold: {new_threshold:.6f}")
                
                if st.button("💾 Save Updated Model", key="save_model"):
                    save_updated_artifacts(model, scaler, feature_columns, new_threshold)
                    st.success("Model saved successfully!")
        except Exception as e:
            st.error(f"Training failed: {e}")
            st.exception(e)
    else:
        st.info("Please upload a training dataset.")
