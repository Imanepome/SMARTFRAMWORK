import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from datetime import datetime

from ui.sidebar import render_sidebar


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="Alerts Dashboard", layout="wide")


# ==========================================================
# SIDEBAR + ROLE ACCESS
# ==========================================================
render_sidebar(st.session_state.role)


def require_role(allowed_roles):
    if "role" not in st.session_state or st.session_state.role not in allowed_roles:
        st.error("Access Denied.")
        st.stop()


require_role(["admin", "faults_manager","turbine_manager","maintenance"])


# ==========================================================
# CSS — UPDATED FULL BLOCK (BLACK TEXT + RED ACTIVE + GREEN RESOLVED)
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, .stApp { background: white !important; }
.block-container { padding: 1.75rem 2.5rem 3rem !important; max-width: 100% !important; }
[data-testid="stSidebarNav"] { display: none; }
section[data-testid="stSidebar"] { padding-top: 16px; background: #fff; border-right: 1px solid #E2E6EE; }

/* ── header ── */
.dash-header {
    padding-bottom: 1.25rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #E2E6EE;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
}
.dash-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem; font-weight: 700;
    color: #0F1623; margin-bottom: 4px;
    display: flex; align-items: center; gap: 10px;
}
.dash-sub {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #111827;  /* ✅ BLACK */
}
.live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 600; letter-spacing: .04em;
    color: #166534; background: #F0FDF4;
    border: 1px solid #BBF7D0; padding: 3px 10px; border-radius: 99px;
}
.live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #22C55E; animation: lp 2s infinite;
}
@keyframes lp { 0%,100%{opacity:1;} 50%{opacity:.2;} }

/* ── KPI cards ── */
.kpi {
    padding: 18px 20px;
    border-radius: 14px;
    background: #fff;
    border: 1px solid #E2E6EE;
    border-top: 3px solid #E2E6EE;
    font-weight: bold;
    transition: box-shadow .2s;
}
.kpi:hover { box-shadow: 0 4px 20px rgba(0,0,0,.08); }

.kpi h2 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important; font-weight: 700 !important;
    margin: 0 0 4px 0 !important; color: inherit !important;
}
.kpi p {
    font-family: 'Inter', sans-serif;
    font-size: 11px !important; font-weight: 500 !important;
    color: #111827 !important;  /* ✅ BLACK */
    text-transform: uppercase;
    letter-spacing: .06em; margin: 0 !important;
}

.total   { border-top-color: #EF4444; }
.total h2 { color: #EF4444 !important; }

/* ✅ ACTIVE KPI RED + GLOW */
.active  {
    border-top-color: #EF4444;
    box-shadow: 0 0 18px rgba(239,68,68,0.35);
}
.active h2 { color: #EF4444 !important; }

/* ✅ RESOLVED KPI GREEN + GLOW */
.resolved {
    border-top-color: #22C55E;
    box-shadow: 0 0 18px rgba(34,197,94,0.35);
}
.resolved h2 { color: #16A34A !important; }

.severe  { border-top-color: #DC2626; }
.severe h2 { color: #DC2626 !important; }

.medium  { border-top-color: #F59E0B; }
.medium h2 { color: #D97706 !important; }

.anomaly { border-top-color: #8B5CF6; }
.anomaly h2 { color: #7C3AED !important; }

/* ── section label ── */
.sec-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px; font-weight: 600;
    color: #111827; /* ✅ BLACK */
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
.panel.active-panel {
    border: 1px solid rgba(239,68,68,0.45);
    box-shadow: 0 0 22px rgba(239,68,68,0.22);
}
.panel-head {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 20px; background: #FAFBFD;
    border-bottom: 1px solid #E2E6EE; flex-wrap: wrap; gap: 8px;
}
.panel-title {
    font-family: 'Inter', sans-serif;
    font-size: 13px; font-weight: 700;
    color: #EF4444; /* ✅ RED */
    display: flex; align-items: center; gap: 8px;
}
.panel-badge {
    font-size: 11px; font-weight: 500;
    color: #111827; /* ✅ BLACK */
    background: #F1F3F8; border: 1px solid #E2E6EE;
    padding: 2px 8px; border-radius: 99px;
}
.panel-hint {
    font-size: 11px;
    color: #111827; /* ✅ BLACK */
    font-style: italic;
}

/* ── alert table ── */
.atbl { width: 100%; border-collapse: collapse; }
.atbl thead th {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 600;
    color: #111827; /* ✅ BLACK */
    text-transform: uppercase; letter-spacing: .07em;
    padding: 10px 16px; text-align: left;
    background: #FAFBFD; border-bottom: 1px solid #E2E6EE;
    white-space: nowrap;
}
.atbl tbody tr { border-bottom: 1px solid #F1F3F8; transition: background .1s; }
.atbl tbody tr:last-child { border-bottom: none; }
.atbl tbody tr:hover { background: #FAFBFD; }
.atbl td {
    padding: 11px 16px; vertical-align: middle;
    font-family: 'Inter', sans-serif; font-size: 13px; color: #111827;
}

/* ✅ ALL LEFT BORDER RED */
.atbl tr.rs td:first-child { border-left: 3px solid #EF4444; }
.atbl tr.rm td:first-child { border-left: 3px solid #EF4444; }
.atbl tr.rl td:first-child { border-left: 3px solid #EF4444; }

/* ── badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 99px;
    font-size: 11px; font-weight: 600;
    font-family: 'Inter', sans-serif; white-space: nowrap;
}
.b-severe   { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.b-medium   { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.b-low      { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.b-active   { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.b-resolved { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.b-anom-yes { background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; }
.b-anom-no  { color: #111827; font-size: 13px; }

.tag {
    font-size: 11px; padding: 3px 8px; border-radius: 6px;
    background: #F1F3F8; color: #111827; border: 1px solid #E2E6EE;
    font-family: 'JetBrains Mono', monospace;
}
.ts-cell {
    font-size: 12px;
    color: #111827; /* ✅ BLACK */
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
}

/* ── history table (dataframe override) ── */
.stDataFrame { border-radius: 10px !important; overflow: hidden; border: 1px solid #E2E6EE !important; }

/* ── buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 500 !important;
    border-radius: 8px !important; border: 1px solid #E2E6EE !important;
    background: #fff !important; color: #111827 !important;
}
.stButton > button:hover { background: #F4F6FA !important; }

/* ── divider ── */
hr { border: none; border-top: 1px solid #E2E6EE !important; margin: 1.25rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# DB CONNECTION
# ==========================================================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="smartgrid_db",
    )


# ==========================================================
# DB FUNCTIONS
# ==========================================================
def fetch_alerts(machine_id=None):
    conn = get_connection()
    if machine_id is None:
        query = """
            SELECT alert_id, machine_id, timestamp, alert_type, message,
                   fault_type, severity, is_anomaly, status
            FROM alerts
            ORDER BY timestamp ASC
        """
        df = pd.read_sql(query, conn)
    else:
        query = """
            SELECT alert_id, machine_id, timestamp, alert_type, message,
                   fault_type, severity, is_anomaly, status
            FROM alerts
            WHERE machine_id = %s
            ORDER BY timestamp ASC
        """
        df = pd.read_sql(query, conn, params=(machine_id,))
    conn.close()
    return df


def update_alert_status(alert_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE alerts SET status=%s WHERE alert_id=%s",
        (new_status, alert_id),
    )
    conn.commit()
    conn.close()


# ==========================================================
# BUILD UNIQUE ALERT EVENTS
# ==========================================================
def build_unique_alert_events(df, gap_seconds=5):
    df = df.copy()
    if df.empty:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["is_anomaly"] = df["is_anomaly"].fillna(0).astype(int)
    df = df.sort_values("timestamp").reset_index(drop=True)

    events = []
    current = df.iloc[0]
    start_time = current["timestamp"]

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]
        time_gap = (row["timestamp"] - prev_row["timestamp"]).total_seconds()

        state_changed = (
            row["fault_type"] != current["fault_type"]
            or row["severity"] != current["severity"]
            or row["is_anomaly"] != current["is_anomaly"]
            or row["alert_type"] != current["alert_type"]
            or row["machine_id"] != current["machine_id"]
        )
        gap_detected = time_gap > gap_seconds

        if state_changed or gap_detected:
            events.append({
                "machine_id": current["machine_id"],
                "alert_type": current["alert_type"],
                "fault_type": current["fault_type"],
                "severity": current["severity"],
                "is_anomaly": current["is_anomaly"],
                "status": current["status"],
                "start_time": start_time,
                "end_time": prev_row["timestamp"],
            })
            current = row
            start_time = row["timestamp"]

    events.append({
        "machine_id": current["machine_id"],
        "alert_type": current["alert_type"],
        "fault_type": current["fault_type"],
        "severity": current["severity"],
        "is_anomaly": current["is_anomaly"],
        "status": current["status"],
        "start_time": start_time,
        "end_time": df.iloc[-1]["timestamp"],
    })

    return pd.DataFrame(events)


# ==========================================================
# PAGE TITLE
# ==========================================================
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">
      🚨 Alerts Dashboard
      <span class="live-pill"><span class="live-dot"></span>Live</span>
    </div>
    <div class="dash-sub">
      This page shows all alerts generated by Fault Prediction and Anomaly Detection {datetime.now().strftime("%d %b %Y, %H:%M")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# LOAD DATA
# ==========================================================
df = fetch_alerts()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["is_anomaly"] = df["is_anomaly"].fillna(0).astype(int)
df = df.sort_values("timestamp", ascending=False)

df = df.drop_duplicates(
    subset=["machine_id", "alert_type", "fault_type", "severity", "is_anomaly", "status"],
    keep="first"
)

df = df.reset_index(drop=True)

if df.empty:
    st.warning("⚠️ No alerts found in the database.")
    st.stop()

df_events = build_unique_alert_events(df, gap_seconds=5)

if df_events.empty:
    st.warning("⚠️ No valid alert events found.")
    st.stop()


# ==========================================================
# METRICS
# ==========================================================
total_alerts = len(df_events)
active_alerts = len(df_events[df_events["status"] == "active"])
resolved_alerts = len(df_events[df_events["status"] == "resolved"])
severe_alerts = len(df_events[df_events["severity"] == "severe"])
medium_alerts = len(df_events[df_events["severity"] == "medium"])
anomaly_alerts = len(df_events[df_events["is_anomaly"] == 1])

col1, col2, col3, col4, col5, col6 = st.columns(6)


def card(title, value, style):
    st.markdown(
        f'<div class="kpi {style}"><h2>{value}</h2><p>{title}</p></div>',
        unsafe_allow_html=True,
    )


with col1: card("Total Alerts", total_alerts, "total")
with col2: card("Active Alerts", active_alerts, "active")
with col3: card("Resolved", resolved_alerts, "resolved")
with col4: card("Severe", severe_alerts, "severe")
with col5: card("Medium", medium_alerts, "medium")
with col6: card("Anomaly Alerts", anomaly_alerts, "anomaly")

st.markdown("---")


# ==========================================================
# CURRENT LATEST ACTIVE ALERTS
# ==========================================================
st.markdown('<div class="sec-label">🔥 Current latest alerts Only different states</div>',
            unsafe_allow_html=True)

df_active = df_events[df_events["status"] == "active"].copy()

if df_active.empty:
    st.success("✅ System is stable  No active alerts detected.")

else:
    df_active_display = df_active.sort_values("end_time", ascending=False).copy()
    df_active_display["Last Detected"] = df_active_display["end_time"]

    df_active_display = df_active_display.rename(columns={
        "alert_type": "Alert Type",
        "fault_type": "Fault Type",
        "severity": "Severity",
        "is_anomaly": "Is Anomaly",
        "machine_id": "Machine ID",
    })

    df_active_display = df_active_display.drop(columns=["start_time", "end_time"], errors="ignore")

    df_active_display = df_active_display[
        ["Machine ID", "Alert Type", "Fault Type", "Severity", "Is Anomaly", "Last Detected"]
    ]

    def sev_badge(s):
        s = str(s).lower()
        cls = {"severe": "b-severe", "medium": "b-medium"}.get(s, "b-low")
        return f'<span class="badge {cls}">{s.capitalize()}</span>'

    def anom_badge(v):
        if int(v):
            return '<span class="badge b-anom-yes">▲ Yes</span>'
        return '<span class="b-anom-no">—</span>'

    def row_cls(sev):
        return {"severe": "rs", "medium": "rm"}.get(str(sev).lower(), "rl")

    rows = ""
    for _, r in df_active_display.iterrows():
        ts = r["Last Detected"].strftime("%Y-%m-%d %H:%M") if pd.notna(r["Last Detected"]) else "—"
        rc = row_cls(r["Severity"])
        mid = str(int(r["Machine ID"])) if pd.notna(r["Machine ID"]) else "—"

        rows += f"""
        <tr class="{rc}">
          <td style="font-size:12px;color:#111827;font-family:'JetBrains Mono',monospace;">#{mid}</td>
          <td><span class="tag">{r['Alert Type'] or '—'}</span></td>
          <td><span class="tag">{r['Fault Type'] or '—'}</span></td>
          <td>{sev_badge(r['Severity'])}</td>
          <td>{anom_badge(r['Is Anomaly'])}</td>
          <td class="ts-cell">{ts}</td>
        </tr>"""

    st.markdown(f"""
    <div class="panel active-panel">
      <div class="panel-head">
        <div class="panel-title">
          🔴 Active alert states
          <span class="panel-badge">{len(df_active_display)} unique</span>
        </div>
        <span class="panel-hint">Sorted by most recently detected</span>
      </div>
      <div style="overflow-x:auto;">
        <table class="atbl">
          <thead><tr>
            <th style="width:80px;">Machine</th>
            <th style="width:130px;">Alert type</th>
            <th style="width:130px;">Fault type</th>
            <th style="width:95px;">Severity</th>
            <th style="width:85px;">Anomaly</th>
            <th style="width:140px;">Last detected</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ==========================================================
# ALERT TREND
# ==========================================================
st.subheader("🔴 Alert Trend Over Time")

trend_df = df_events.groupby(df_events["start_time"].dt.date).size().reset_index(name="alerts_count")
trend_df.columns = ["date", "alerts"]

fig_trend = px.line(
    trend_df, x="date", y="alerts", markers=True,
    title="Alerts Trend Over Time (Unique Events)",
)

fig_trend.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#111827", family="Inter"),
)

st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")


# ==========================================================
# MACHINE HEALTH SCORE
# ==========================================================
st.subheader("🟢 Machine Health Score")


def compute_health(group):
    score = 100
    score -= group[group["severity"] == "severe"].shape[0] * 8
    score -= group[group["severity"] == "medium"].shape[0] * 4
    score -= group[group["is_anomaly"] == 1].shape[0] * 8
    return max(score, 0)


health_scores = df_events.groupby("machine_id").apply(compute_health).reset_index()
health_scores.columns = ["machine_id", "health_score"]
bar_colors = [
    "#EF4444" if s < 50 else "#F59E0B" if s < 85 else "#22C55E"
    for s in health_scores["health_score"]
]
fig_health = px.bar(
    health_scores,
    x="machine_id",
    y="health_score",
    text="health_score",
    title="Machine Health Score (%)  Unique Events",
)

fig_health.update_traces(
    textposition="outside",
    marker_color=bar_colors 
)

fig_health.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#2E531C", family="Inter"),
    yaxis_range=[0, 115],
)

st.plotly_chart(fig_health, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")


# ==========================================================
# ANALYTICS DASHBOARD
# ==========================================================
st.markdown("## 📊 Alerts Analytics Dashboard")
st.markdown("##### Realtime insights from system alerts")

colc1, colc2 = st.columns(2)

colors = {
    "severe": "#EF4444",
    "medium": "#F59E0B",
    "active": "#EF4444",     # 🔴 RED
    "resolved":"#22C55E",   # 🟢 GREEN
    "anomaly": "#EE642E",
}

sev_df = df_events[df_events["severity"].notna()]

with colc1:
    st.markdown("### ⚠️ Severity Distribution")
    if not sev_df.empty:
        fig_sev = px.histogram(
            sev_df,
            x="severity",
            color="severity",
            text_auto=True,
            color_discrete_map={
                "severe": colors["severe"],
                "medium": colors["medium"]
            },
        )

        fig_sev.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#FFFFFF", family="Inter"),
            showlegend=False,
        )

        st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No severity data available.")

with colc2:
    st.markdown("### 🔄 Alerts Status Overview")
    df_status = df_events.copy()
    df_status["status"] = df_status["status"].str.lower()

    status_order = ["active", "resolved"]

    fig_status = px.pie(
    df_status,
    names="status",
    hole=0.55,
    category_orders={"status": status_order},
)

    fig_status.update_traces(
    textposition="inside",
    textinfo="percent+label",
    marker=dict(
        colors=["#EF4444", "#22C55E"]  # active = red, resolved = green
    ),
    textfont=dict(size=12),
)

    fig_status.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#F1F2F5", family="Inter"),
        showlegend=True,
    )

    st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")


# ==========================================================
# FULL ALERT HISTORY TABLE
# ==========================================================
st.subheader("🗂️ Alerts History (Unique Events)")

df_history = df_events.sort_values("end_time", ascending=False).copy()
df_history["Last Detected"] = df_history["end_time"]

df_history = df_history.rename(columns={
    "machine_id": "Machine ID",
    "alert_type": "Alert Type",
    "fault_type": "Fault Type",
    "severity": "Severity",
    "is_anomaly": "Is Anomaly",
    "status": "Status",
})

df_history = df_history.drop(columns=["start_time", "end_time"], errors="ignore")

df_history = df_history[
    ["Machine ID", "Alert Type", "Fault Type", "Severity", "Is Anomaly", "Status", "Last Detected"]
]

st.dataframe(df_history, use_container_width=True)