import streamlit as st
import pandas as pd
from datetime import datetime

from ui.sidebar import render_sidebar
from db_queries import (
    fetch_active_alerts,
    insert_maintenance_action,
    fetch_maintenance_history,
    update_alert_status_group
)

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="Maintenance Dashboard", layout="wide")

# ==========================================================
# SIDEBAR + ROLE ACCESS
# ==========================================================
render_sidebar(st.session_state.role) if "role" in st.session_state else None

def require_role(allowed_roles):
    if "role" not in st.session_state or st.session_state.role not in allowed_roles:
        st.error("⛔ Access Denied.")
        st.stop()

require_role(["admin", "maintenance"])

# ==========================================================
# CSS — single clean block (UPDATED)
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, .stApp          { background: white !important; }
.block-container            { padding: 1.75rem 2.5rem 3rem !important; max-width: 100% !important; }
[data-testid="stSidebarNav"]{ display: none; }
section[data-testid="stSidebar"] {
    padding-top: 16px; background: #fff; border-right: 1px solid #E2E6EE;
}
            /* ── LOGOUT BUTTON BLUE ── */
div.stButton > button {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    width: 100% !important;
    padding: 10px !important;
}

/* hover */
div.stButton > button:hover {
    background-color: #3B82F6 !important;
    color: white !important;
}

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
.pg-sub { font-size: 13px; color: #111827; font-family: 'Inter', sans-serif; margin-top: 3px; font-weight: 500; }

.header-right {
    display: flex;
    align-items: center;
    gap: 12px;
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

/* ── section label ── */
.sec-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px; font-weight: 700; color: #111827;
    text-transform: uppercase; letter-spacing: .08em;
    padding-bottom: 8px; margin-bottom: 14px;
    border-bottom: 1px solid #E2E6EE;
    display: flex; align-items: center; gap: 6px;
}

/* ── panel ── */
.panel {
    background: #fff; border: 1px solid #E2E6EE;
    border-radius: 14px; overflow: hidden; margin-bottom: 1.25rem;
}

/* glow red for active alerts table */
.panel.glow-red {
    border: 1px solid rgba(239,68,68,0.45) !important;
    box-shadow: 0 0 22px rgba(239,68,68,0.18) !important;
}

.panel-head {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 20px; background: #FAFBFD;
    border-bottom: 1px solid #E2E6EE; flex-wrap: wrap; gap: 8px;
}
.panel-title {
    font-family: 'Inter', sans-serif;
    font-size: 13px; font-weight: 700; color: #0F1623;
    display: flex; align-items: center; gap: 8px;
}
.panel-badge {
    font-size: 11px; font-weight: 600; color: #111827;
    background: #F1F3F8; border: 1px solid #E2E6EE;
    padding: 2px 8px; border-radius: 99px;
}
.panel-hint { font-size: 11px; color: #111827; font-style: italic; font-weight: 500; }

/* ── alert table ── */
.atbl { width: 100%; border-collapse: collapse; }
.atbl thead th {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 800; color: #111827;
    text-transform: uppercase; letter-spacing: .07em;
    padding: 10px 16px; text-align: left;
    background: #FAFBFD; border-bottom: 1px solid #E2E6EE; white-space: nowrap;
}
.atbl tbody tr { border-bottom: 1px solid #F1F3F8; transition: background .1s; }
.atbl tbody tr:last-child { border-bottom: none; }
.atbl tbody tr:hover { background: #FAFBFD; }
.atbl td { padding: 11px 16px; vertical-align: middle;
           font-family: 'Inter', sans-serif; font-size: 13px; color: #111827; }

/* left border indicators */
.atbl tr.rs td:first-child { border-left: 3px solid #EF4444; }
.atbl tr.rm td:first-child { border-left: 3px solid #F59E0B; }
.atbl tr.rl td:first-child { border-left: 3px solid #EF4444; }

/* ── badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 99px;
    font-size: 11px; font-weight: 700;
    font-family: 'Inter', sans-serif; white-space: nowrap;
}
.b-severe   { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.b-medium   { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.b-low      { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.b-anom-yes { background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; }
.b-anom-no  { color: #111827; font-size: 13px; font-weight: 700; }

.b-pending     { background: #FFF7ED; color: #9A3412; border: 1px solid #FED7AA; }
.b-active-s    { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.b-resolved    { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }

.sdot   { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 5px; vertical-align: middle; }
.sdot-a { background: #EF4444; } .sdot-r { background: #22C55E; }

.tag {
    font-size: 11px; padding: 3px 8px; border-radius: 6px;
    background: #F1F3F8; color: #111827; border: 1px solid #E2E6EE;
    font-family: 'JetBrains Mono', monospace;
}
.ts-cell { font-size: 12px; color: #111827; font-family: 'JetBrains Mono', monospace; white-space: nowrap; }

/* ── selected alert info bar ── */
.alert-info-bar {
    display: flex; align-items: center; flex-wrap: wrap; gap: 10px;
    background: #EFF6FF; border: 1px solid #BFDBFE;
    border-radius: 10px; padding: 10px 16px; margin-bottom: 16px;
    font-family: 'Inter', sans-serif; font-size: 12px; color: #1E40AF;
}
.alert-info-bar strong { font-weight: 700; }
.info-sep { color: #93C5FD; }

/* ── cost metric ── */
.cost-metric {
    background: #F0FDF4; border: 1px solid #BBF7D0;
    border-radius: 10px; padding: 12px 18px;
    font-family: 'Inter', sans-serif;
}
.cost-label { font-size: 11px; font-weight: 700; color: #166534;
              text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }
.cost-value { font-family: 'JetBrains Mono', monospace;
              font-size: 24px; font-weight: 800; color: #15803D; }

/* ── history table ── */
.stDataFrame { border-radius: 10px !important; overflow: hidden;
               border: 1px solid #E2E6EE !important; }

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: transparent; border-bottom: 1px solid #E2E6EE;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
    color: #111827 !important; background: transparent !important;
    border: none !important; border-radius: 8px 8px 0 0 !important;
    padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] {
    color: #0F1623 !important; background: #fff !important;
    border: 1px solid #E2E6EE !important; border-bottom: 1px solid #fff !important;
    font-weight: 800 !important;
}

/* ── buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
    border-radius: 8px !important; border: 1px solid #E2E6EE !important;
    background: #fff !important; color: #111827 !important;
}
.stButton > button:hover { background: #F4F6FA !important; }

/* ── SAVE BUTTON BLUE (FORM STYLE) ── */
div[data-testid="stForm"] button {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    width: 100% !important;
    padding: 10px !important;
    
}

div[data-testid="stForm"] button:hover {
    background-color: #3B82F6 !important;
    color: white !important;
}

/* ── form inputs (CUSTOM COLORS) ── */

/* ORANGE warm borders (Performed by, Part replaced, Cost, Description Notes) */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    border: 1.7px solid #FB923C !important;
    background: #fff !important;
    color: black !important;
    box-shadow: 0 0 0px rgba(251,146,60,0) !important;
}

/* Orange focus glow */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border: 2px solid #F97316 !important;
    box-shadow: 0 0 12px rgba(249,115,22,0.35) !important;
}

/* BLUE cold borders (Action type + Maintenance status selectbox) */
.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1.7px solid #60A5FA !important;
    background: #fff !important;
}

/* Selectbox text gray */
.stSelectbox div[data-baseweb="select"] span {
    color: #6B7280 !important;
    font-weight: 600 !important;
}

/* Blue focus glow */
.stSelectbox > div > div:focus-within {
    border: 2px solid #3B82F6 !important;
    box-shadow: 0 0 14px rgba(59,130,246,0.35) !important;
}

hr { border: none; border-top: 1px solid #E2E6EE !important; margin: 1.25rem 0 !important; }
 /* ── LOGOUT BUTTON ── */
/* ── LOGOUT BUTTON FIX (FOR STREAMLIT BASE BUTTON) ── */
button[kind="primary"] {
    background-color: #2563EB !important;
    color: white !important;
}

/* force inner text color */
button[kind="primary"] * {
    color: white !important;
}

/* hover */
button[kind="primary"]:hover {
    background-color: #3B82F6 !important;
    color: white !important;
}


</style>
""", unsafe_allow_html=True)


# ==========================================================
# PAGE HEADER (LIVE + DATE/TIME NEXT TO TITLE)
# ==========================================================
now_txt = datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">
        🛠️ Maintenance Actions
        <span class="live-pill"><span class="live-dot"></span>Live</span>
        <span class="header-datetime">{now_txt}</span>
    </div>
    <div class="pg-sub">Register and track maintenance actions for active alerts</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# TABS
# ==========================================================
tab1, tab2 = st.tabs(["🚨 Active Alerts", "🗂️ Maintenance History"])

# ==========================================================
# TAB 1: ACTIVE ALERTS
# ==========================================================
with tab1:

    df_alerts = fetch_active_alerts()

    if df_alerts is None or df_alerts.empty:
        st.success("✅ No active alerts. System is stable.")
    else:
        # تجهيز البيانات
        df_alerts["timestamp"]  = pd.to_datetime(df_alerts["timestamp"], errors="coerce")
        df_alerts["fault_type"] = df_alerts["fault_type"].fillna("None")
        df_alerts["severity"]   = df_alerts["severity"].fillna("None")
        df_alerts["alert_type"] = df_alerts["alert_type"].fillna("Unknown")
        df_alerts["message"]    = df_alerts["message"].fillna("")
        df_alerts["is_anomaly"] = df_alerts["is_anomaly"].fillna(0).astype(int)

        df_latest = (
            df_alerts.sort_values("timestamp", ascending=False)
            .drop_duplicates(
                subset=["machine_id", "alert_type", "fault_type", "severity", "is_anomaly"],
                keep="first"
            )
            .reset_index(drop=True)
        )

        # ✅ تظهر فقط Register maintenance action (بدون جدول alerts)
        st.markdown('<div class="sec-label">🛠 Register maintenance action</div>',
                    unsafe_allow_html=True)

        df_latest["label"] = (
            "Machine #" + df_latest["machine_id"].astype(str) + " | "
            + df_latest["alert_type"].astype(str) + " | "
            + "Fault: " + df_latest["fault_type"].astype(str) + " | "
            + "Severity: " + df_latest["severity"].astype(str)
        )

        selected_label = st.selectbox("Select alert to act on", df_latest["label"].tolist())
        selected_df    = df_latest[df_latest["label"] == selected_label]

        if selected_df.empty:
            st.error("⚠️ Selected alert not found. Please refresh the page.")
        else:
            selected_row = selected_df.iloc[0]
            alert_id     = int(selected_row["alert_id"])
            machine_id   = int(selected_row["machine_id"])
            alert_type   = selected_row["alert_type"]
            fault_type   = selected_row["fault_type"]
            severity     = selected_row["severity"]
            is_anomaly   = int(selected_row["is_anomaly"])

            sev_color = {"severe": "#991B1B", "medium": "#92400E"}.get(severity.lower(), "#166534")

            st.markdown(f"""
            <div class="alert-info-bar">
              <strong>Machine #{machine_id}</strong>
              <span class="info-sep">|</span>
              <span>{alert_type}</span>
              <span class="info-sep">|</span>
              <span>Fault: <strong>{fault_type}</strong></span>
              <span class="info-sep">|</span>
              <span>Severity: <strong style="color:{sev_color};">{severity.capitalize()}</strong></span>
              <span class="info-sep">|</span>
              <span>Anomaly: <strong>{"Yes" if is_anomaly else "No"}</strong></span>
            </div>
            """, unsafe_allow_html=True)

            with st.form("maintenance_form"):

                c1, c2, c3 = st.columns(3)
                with c1:
                    action_type = st.selectbox(
                        "Action type",
                        ["Inspection","Repair","Replacement","Calibration","Shutdown","Other"]
                    )
                with c2:
                    status = st.selectbox(
                        "Maintenance status",
                        ["in_progress","completed"]
                    )
                with c3:
                    performed_by = st.text_input("Performed by", placeholder="Technician name")

                c4, c5 = st.columns([2, 1])
                with c4:
                    part_replaced = st.text_input("Part replaced", placeholder="Leave blank if not applicable")
                with c5:
                    cost = st.number_input("Cost ($)", min_value=0.0, step=10.0)

                description = st.text_area(
                    "Description / Notes",
                    placeholder="Describe the maintenance action performed…",
                    height=90
                )

                submit = st.form_submit_button("💾 Save Maintenance Action")

                if submit:
                    insert_maintenance_action(
                        machine_id    = machine_id,
                        alert_id      = alert_id,
                        timestamp     = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        action_type   = action_type,
                        description   = description,
                        performed_by  = performed_by,
                        part_replaced = part_replaced,
                        cost          = float(cost),
                        status        = status
                    )

                    if status == "completed":
                        update_alert_status_group(
                            machine_id  = machine_id,
                            alert_type  = alert_type,
                            fault_type  = fault_type if fault_type != "None" else None,
                            severity    = severity if severity != "None" else None,
                            is_anomaly  = is_anomaly,
                            new_status  = "resolved"
                        )

                    st.success("✅ Maintenance action saved successfully!")
                    st.rerun()

# ==========================================================
# TAB 2: MAINTENANCE HISTORY
# ==========================================================
with tab2:

    df_history = fetch_maintenance_history()

    if df_history is None or df_history.empty:
        st.warning("No maintenance actions found yet.")
    else:
        total_cost = df_history["cost"].sum()

        mc1, mc2, mc3 = st.columns([1, 1, 4])
        with mc1:
            st.markdown(f"""
            <div class="cost-metric">
              <div class="cost-label">Total cost</div>
              <div class="cost-value">${total_cost:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with mc2:
            st.markdown(f"""
            <div class="cost-metric" style="background:#EFF6FF;border-color:#BFDBFE;">
              <div class="cost-label" style="color:#1D4ED8;">Total actions</div>
              <div class="cost-value" style="color:#1E40AF;">{len(df_history)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        st.dataframe(df_history, use_container_width=True)