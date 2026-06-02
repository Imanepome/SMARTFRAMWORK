import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import io

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="Report", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] { padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

from ui.sidebar import render_sidebar
render_sidebar(st.session_state.role)

# ==========================================================
# CSS
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, .stApp { background: white !important; }
.block-container { padding: 1.75rem 2.5rem 3rem !important; max-width: 100% !important; }

/* ── page header ── */
.pg-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1.25rem; margin-bottom: 1.5rem;
    border-bottom: 2px solid #E2E6EE; flex-wrap: wrap; gap: 10px;
}
.pg-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.55rem; font-weight: 800; color: #0F1623;
    display: flex; align-items: center; gap: 10px;
}
.pg-sub { font-size: 13px; color: #6B7280; font-family: 'Inter', sans-serif; margin-top: 3px; }
.header-datetime {
    font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #111827;
    background: #fff; border: 1px solid #E2E6EE; padding: 6px 10px; border-radius: 10px;
}
.live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 700; color: #166534; background: #F0FDF4;
    border: 1px solid #BBF7D0; padding: 4px 12px; border-radius: 99px;
}
.live-dot { width: 7px; height: 7px; border-radius: 50%;
            background: #22C55E; animation: lp 2s infinite; }
@keyframes lp { 0%,100%{opacity:1;} 50%{opacity:.2;} }

/* ── section title ── */
.sec-title {
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800;
    color: #374151; text-transform: uppercase; letter-spacing: .1em;
    padding: 0 0 10px 0; margin-bottom: 16px;
    border-bottom: 2px solid #E2E6EE;
    display: flex; align-items: center; gap: 8px;
}

/* ── risk badge ── */
.risk-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 99px;
    font-size: 12px; font-weight: 800; letter-spacing: .05em;
}
.risk-high   { background: #FEE2E2; color: #991B1B; border: 1.5px solid #FECACA; }
.risk-medium { background: #FEF3C7; color: #92400E; border: 1.5px solid #FDE68A; }
.risk-low    { background: #DCFCE7; color: #166534; border: 1.5px solid #BBF7D0; }
.risk-unsafe { background: #FEE2E2; color: #991B1B; border: 1.5px solid #FECACA; }

/* ── decision cards ── */
.dec-card {
    border-radius: 10px; padding: 14px 18px;
    margin-bottom: 10px; border-left: 4px solid;
}
.dec-urgent  { background: #FFF5F5; border-color: #FC8181; }
.dec-warning { background: #FFFBEB; border-color: #FBBF24; }
.dec-ok      { background: #F0FDF4; border-color: #4ADE80; }
.dec-unsafe  { background: #FFF5F5; border-color: #FC8181; }
.dec-title   { font-size: 14px; font-weight: 700; margin-bottom: 4px; color: #111827; }
.dec-detail  { font-size: 13px; color: #6B7280; line-height: 1.6; }

/* ── metrics grid ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
/* ── metrics grid ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: white;
    border: 1px solid #60A5FA;  /* تغيير لون الحافة إلى أزرق فاتح */
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 0 8px rgba(96, 165, 250, 0.3);  /* إضافة تأثير الإشعاع */
    transition: box-shadow 0.2s ease;
}
.metric-card:hover {
    box-shadow: 0 0 12px rgba(96, 165, 250, 0.5);  /* تكثيف الإشعاع عند المرور */
}
.metric-label {
    font-size: 0.7rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 0.5rem;
}
.metric-label {
    font-size: 0.7rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 0.5rem;
}

hr { border: none; border-top: 1px solid #E2E6EE !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# DB
# ==========================================================
def get_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="smartgrid_db"
    )

def fetch_alerts_by_date_range(machine_id=None, start_date=None, end_date=None):
    """جلب التنبيهات حسب نطاق زمني محدد"""
    conn = get_connection()
    query = """
        SELECT alert_id, machine_id, timestamp, alert_type, message,
               fault_type, severity, is_anomaly, status
        FROM alerts
        WHERE 1=1
    """
    params = []
    
    if machine_id:
        query += " AND machine_id = %s"
        params.append(machine_id)
    if start_date:
        query += " AND timestamp >= %s"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= %s"
        params.append(end_date)
    
    query += " ORDER BY timestamp ASC"
    
    try:
        df = pd.read_sql(query, conn, params=params)
    except Exception as e:
        st.warning(f"Could not fetch alerts: {e}")
        df = pd.DataFrame()
    
    conn.close()
    
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["is_anomaly"] = df["is_anomaly"].fillna(0).astype(int)
    
    return df

def fetch_maintenance_cost_by_date_range(machine_id=None, start_date=None, end_date=None):
    """جلب تكاليف الصيانة حسب نطاق زمني"""
    conn = get_connection()
    query = """
        SELECT cost, machine_id, timestamp
        FROM maintenance_actions
        WHERE 1=1
    """
    params = []
    
    if machine_id:
        query += " AND machine_id = %s"
        params.append(machine_id)
    if start_date:
        query += " AND timestamp >= %s"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= %s"
        params.append(end_date)
    
    try:
        df = pd.read_sql(query, conn, params=params)
    except Exception as e:
        st.warning(f"Could not fetch maintenance data: {e}")
        df = pd.DataFrame()
    
    conn.close()
    
    if not df.empty and "cost" in df.columns:
        total = float(df["cost"].sum())
        count = len(df)
    else:
        total = 0.0
        count = 0
    
    return total, count

def build_unique_alert_events(df, gap_seconds=5):
    df = df.copy()
    if df.empty:
        return pd.DataFrame()
    df["timestamp"]  = pd.to_datetime(df["timestamp"])
    df["is_anomaly"] = df["is_anomaly"].fillna(0).astype(int)
    df = df.sort_values("timestamp").reset_index(drop=True)
    events = []
    if len(df) == 0:
        return pd.DataFrame()
    current = df.iloc[0]
    start_time = current["timestamp"]
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        gap = (row["timestamp"] - prev["timestamp"]).total_seconds()
        changed = (
            row["fault_type"] != current["fault_type"] or
            row["severity"]   != current["severity"]   or
            row["is_anomaly"] != current["is_anomaly"] or
            row["alert_type"] != current["alert_type"] or
            row["machine_id"] != current["machine_id"]
        )
        if changed or gap > gap_seconds:
            events.append({
                "machine_id": current["machine_id"],
                "alert_type": current["alert_type"],
                "fault_type": current["fault_type"],
                "severity": current["severity"],
                "is_anomaly": current["is_anomaly"],
                "status": current["status"],
                "start_time": start_time,
                "end_time": prev["timestamp"]
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
        "end_time": df.iloc[-1]["timestamp"]
    })
    return pd.DataFrame(events)

def save_report(machine_id, report_type, metrics, summary, period_start, period_end):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO reports (machine_id, created_at, created_by, report_type,
            summary, period_start, period_end, health_score,
            total_alerts, total_anomalies, total_cost)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (machine_id, "system", report_type, summary,
              period_start, period_end,
              metrics["health"], metrics["total"], metrics["anomalies"], metrics["cost"]))
        conn.commit()
        st.success("✅ Report saved successfully!")
    except Exception as e:
        st.warning(f"Could not save report: {e}")
    finally:
        cur.close()
        conn.close()

def export_pdf(lbl, period_label, metrics, decisions):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    st_ = getSampleStyleSheet()
    ts  = ParagraphStyle("T", parent=st_["Heading1"], fontSize=18, spaceAfter=4,
                         textColor=colors.HexColor("#111827"))
    h2  = ParagraphStyle("H", parent=st_["Heading2"], fontSize=13,
                         spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#374151"))
    bs  = ParagraphStyle("B", parent=st_["Normal"], fontSize=10, leading=15,
                         textColor=colors.HexColor("#374151"))
    ms  = ParagraphStyle("M", parent=st_["Normal"], fontSize=9,
                         textColor=colors.HexColor("#6B7280"))
    content = []

    content.append(Paragraph(f"Report ({period_label})", ts))
    content.append(Paragraph(
        f"{lbl} &nbsp;|&nbsp; Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", ms))
    content.append(Spacer(1, 0.3*cm))
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#E5E7EB")))
    content.append(Spacer(1, 0.4*cm))

    rmap = {"HIGH RISK":"#DC2626","MEDIUM RISK":"#D97706","LOW RISK":"#16A34A","UNSAFE":"#DC2626"}
    rc   = rmap.get(metrics["risk"], "#374151")
    content.append(Paragraph(
        f'Status: <font color="{rc}"><b>{metrics["risk"]}</b></font>'
        f'&nbsp;&nbsp; Overall Health: <b>{metrics["health"]}/100</b>', bs))
    content.append(Spacer(1, 0.5*cm))

    content.append(Paragraph("Key Metrics", h2))
    kpi_rows = [
        ["Metric", "Value"],
        ["Total Alert Events",  str(metrics["total"])],
        ["Active Alerts",       str(metrics["active"])],
        ["Resolved Alerts",     str(metrics["resolved"])],
        ["Severe Alerts",       str(metrics["severe"])],
        ["Medium Alerts",       str(metrics["medium"])],
        ["Anomaly Alerts",      str(metrics["anomalies"])],
        ["Overall Health Score",f"{metrics['health']}/100"],
        ["Total Maintenance Cost", f"${metrics['cost']:,.2f}"],
        ["Maintenance Actions", str(metrics.get("maintenance_count", 0))],
    ]
    tbl_s = TableStyle([
        ("BACKGROUND",     (0,0),(-1,0),  colors.HexColor("#F3F4F6")),
        ("FONTNAME",       (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("GRID",           (0,0),(-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ("LEFTPADDING",    (0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
        ("TOPPADDING",     (0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ])
    t = Table(kpi_rows, colWidths=[8*cm, 6*cm])
    t.setStyle(tbl_s)
    content.append(t)
    content.append(Spacer(1, 0.5*cm))

    content.append(Paragraph("Decision Support", h2))
    icons = {"urgent":"⚠","warning":"→","ok":"✓","unsafe":"🔴"}
    for level, title, detail in decisions:
        content.append(Paragraph(f"{icons.get(level,'•')}  {title}", bs))
        content.append(Paragraph(f"   {detail}", ms))
        content.append(Spacer(1, 0.2*cm))

    content.append(Spacer(1, 0.4*cm))
    content.append(HRFlowable(width="100%", thickness=0.5,
                               color=colors.HexColor("#E5E7EB")))
    
    doc.build(content)
    buf.seek(0)
    return buf

# ==========================================================
# HEADER
# ==========================================================
now_txt = datetime.now().strftime("%d %b %Y · %H:%M")
st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">
      📑 Report Decision Support
      <span class="live-pill"><span class="live-dot"></span>Live</span>
      <span class="header-datetime">{now_txt}</span>
    </div>
    <div class="pg-sub">
      Professional report based on Alerts and Maintenance Dashboard 
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# CONTROLS
# ==========================================================
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
with c1:
    machine_id_input = st.number_input(
        "Machine ID (0 = All machines)",
        value=42, min_value=0, step=1
    )
with c2:
    period_type = st.selectbox(
        "Report Period",
        ["daily", "weekly", "monthly"],
        format_func=lambda x: {"daily": "📅 Daily (Last 24h)", 
                               "weekly": "📆 Weekly (Last 7 days)", 
                               "monthly": "📊 Monthly (Last 30 days)"}[x]
    )
with c3:
    st.markdown("<div style='padding-top:1.6rem'></div>", unsafe_allow_html=True)
    run = st.button("📊 Generate Report", use_container_width=True, type="primary")
with c4:
    st.markdown("<div style='padding-top:1.6rem'></div>", unsafe_allow_html=True)
    auto_ref = st.checkbox("Auto-refresh (60s)", value=False)

if auto_ref:
    import time
    time.sleep(60)
    st.rerun()

# ==========================================================
# MAIN
# ==========================================================
if run:
    # تحديد نطاق التاريخ بناءً على type
    now = datetime.now()
    if period_type == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Daily (Last 24 Hours)"
    elif period_type == "weekly":
        start_date = now - timedelta(days=7)
        period_label = "Weekly (Last 7 Days)"
    else:
        start_date = now - timedelta(days=30)
        period_label = "Monthly (Last 30 Days)"
    
    end_date = now
    start_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    mid = None if machine_id_input == 0 else int(machine_id_input)
    lbl = "All Machines" if mid is None else f"Machine #{mid}"
    
    with st.spinner(f"Loading data for {period_label}..."):
        try:
            # جلب البيانات حسب النطاق الزمني
            df_raw = fetch_alerts_by_date_range(machine_id=mid, start_date=start_str, end_date=end_str)
            total_cost, total_actions = fetch_maintenance_cost_by_date_range(machine_id=mid, start_date=start_str, end_date=end_str)
            
            if df_raw.empty:
                st.warning(f"⚠️ No alerts found for {lbl} in the selected period ({period_label}).")
                # إنشاء بيانات فارغة للتعامل معها
                total_alerts = 0
                active_alerts = 0
                resolved_alerts = 0
                severe_alerts = 0
                medium_alerts = 0
                anomaly_alerts = 0
                overall_health = 100
                has_any_alert = False
                has_anomaly = False
                has_severe = False
                has_medium_only = False
                has_maintenance = total_actions > 0
                df_events = pd.DataFrame()
            else:
                df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])
                df_raw["is_anomaly"] = df_raw["is_anomaly"].fillna(0).astype(int)
                df_raw = df_raw.sort_values("timestamp", ascending=False)
                df_raw = df_raw.drop_duplicates(
                    subset=["machine_id", "alert_type", "fault_type",
                            "severity", "is_anomaly", "status"],
                    keep="first"
                ).reset_index(drop=True)
                df_events = build_unique_alert_events(df_raw, gap_seconds=5)
                
                if df_events.empty:
                    total_alerts = 0
                    active_alerts = 0
                    resolved_alerts = 0
                    severe_alerts = 0
                    medium_alerts = 0
                    anomaly_alerts = 0
                    overall_health = 100
                else:
                    total_alerts = len(df_events)
                    active_alerts = len(df_events[df_events["status"] == "active"])
                    resolved_alerts = len(df_events[df_events["status"] == "resolved"])
                    severe_alerts = len(df_events[df_events["severity"] == "severe"])
                    medium_alerts = len(df_events[df_events["severity"] == "medium"])
                    anomaly_alerts = len(df_events[df_events["is_anomaly"] == 1])
                    
                    # حساب درجة الصحة
                    health_score = 100
                    health_score -= severe_alerts * 8
                    health_score -= medium_alerts * 4
                    health_score -= anomaly_alerts * 8
                    overall_health = max(0, min(100, health_score))
            
            has_any_alert = total_alerts > 0
            has_anomaly = anomaly_alerts > 0
            has_severe = severe_alerts > 0
            has_medium_only = (medium_alerts > 0) and (severe_alerts == 0) and (anomaly_alerts == 0)
            has_maintenance = total_actions > 0
            
            # ==========================================================
            # DECISION SUPPORT LOGIC
            # ==========================================================
            decisions = []
            
            # حالة عدم وجود أي Alert
            if not has_any_alert:
                risk = "LOW RISK"
                risk_cls = "risk-low"
                decisions.append(("ok", "🟢 SYSTEM GOOD - No Alerts Detected",
                    f"The system is operating normally with no alerts for {period_label}. "
                    f"All metrics are within acceptable ranges. Continue monitoring."))
            
            # حالة وجود Anomaly أو Severe (HIGH RISK)
            elif has_anomaly or has_severe:
                risk = "HIGH RISK"
                risk_cls = "risk-high"
                decisions.append(("urgent", "🔴 HIGH RISK - Immediate Action Required",
                    f"⚠️ DETECTED: {anomaly_alerts} Anomaly(ies) and {severe_alerts} Severe Alert(s). "
                    f"Immediate maintenance intervention required to prevent system failure."))
            
            # حالة وجود Medium فقط (MEDIUM RISK)
            elif has_medium_only:
                risk = "MEDIUM RISK"
                risk_cls = "risk-medium"
                decisions.append(("warning", "🟠 MEDIUM RISK - Monitor Closely",
                    f"⚠️ {medium_alerts} Medium severity alert(s) detected. "
                    f"No severe or anomaly alerts. Schedule inspection within 48 hours."))
            
            # حالة وجود Alerts بدون Maintenance (حالة غير صحية)
            elif has_any_alert and not has_maintenance:
                risk = "UNSAFE"
                risk_cls = "risk-unsafe"
                decisions.append(("unsafe", "🔴 UNSAFE CONDITION - No Maintenance Recorded",
                    f"⚠️ {total_alerts} alert(s) detected but NO maintenance actions have been recorded. "
                    f"This is an unsafe condition. Schedule maintenance inspection immediately!"))
            
            else:
                risk = "MEDIUM RISK"
                risk_cls = "risk-medium"
                decisions.append(("warning", "🟠 Requires Attention",
                    f"{total_alerts} alert(s) detected. Review and address within scheduled maintenance window."))
            
            metrics = dict(
                total=total_alerts,
                active=active_alerts,
                resolved=resolved_alerts,
                severe=severe_alerts,
                medium=medium_alerts,
                anomalies=anomaly_alerts,
                cost=total_cost,
                health=overall_health,
                risk=risk,
                risk_cls=risk_cls,
                maintenance_count=total_actions
            )
            
            # تخزين في session state
            st.session_state.update({
                "rp_df": df_raw if 'df_raw' in dir() else pd.DataFrame(),
                "rp_events": df_events if 'df_events' in dir() else pd.DataFrame(),
                "rp_metrics": metrics,
                "rp_decisions": decisions,
                "rp_lbl": lbl,
                "rp_period": period_label,
                "rp_start": start_str,
                "rp_end": end_str,
                "rp_period_type": period_type,
                "rp_mid": mid,
            })
            
            st.success(f"✅ Report generated for {period_label}!")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

# عرض التقرير إذا تم إنشاؤه
if "rp_metrics" in st.session_state and st.session_state.rp_metrics is not None:
    
    metrics = st.session_state["rp_metrics"]
    decisions = st.session_state["rp_decisions"]
    lbl = st.session_state["rp_lbl"]
    period_label = st.session_state.get("rp_period", "Report")
    period_type = st.session_state.get("rp_period_type", "daily")
    mid = st.session_state.get("rp_mid", None)
    
    
    
    # ==========================================================
    # SECTION 1 — KEY METRICS (6 مربعات)
    # ==========================================================
    st.markdown('<div class="sec-title">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    # 6 مربعات رئيسية
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Total Alert</div>
            <div class="metric-value" style="color:#2563EB;">{metrics['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        anomaly_color = "#DC2626" if metrics['anomalies'] > 0 else "#16A34A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Anomaly Alerts</div>
            <div class="metric-value" style="color:{anomaly_color};">{metrics['anomalies']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 Severe Alerts</div>
            <div class="metric-value" style="color:#DC2626;">{metrics['severe']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        medium_color = "#D97706" if metrics['medium'] > 0 else "#16A34A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟠 Medium Alerts</div>
            <div class="metric-value" style="color:{medium_color};">{metrics['medium']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        resolved_color = "#16A34A" if metrics['resolved'] > 0 else "#9CA3AF"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟢 Resolved Alerts</div>
            <div class="metric-value" style="color:{resolved_color};">{metrics['resolved']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        cost_color = "red" if metrics['cost'] > 5000 else ("orange" if metrics['cost'] > 2000 else "green")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Maintenance Cost</div>
            <div class="metric-value" style="color:{'#DC2626' if cost_color=='red' else ('#D97706' if cost_color=='orange' else '#16A34A')};">${metrics['cost']:,.0f}</div>
            <div class="metric-label" style="font-size:0.6rem;">{metrics.get('maintenance_count', 0)} action(s)</div>
        </div>
        """, unsafe_allow_html=True)
    
    
    # ==========================================================
    # SECTION 2 — DECISION SUPPORT
    # ==========================================================
    st.markdown('<div class="sec-title">🧠 Decision Support</div>', unsafe_allow_html=True)
    
    rc_k = metrics["risk_cls"]
    st.markdown(
        f'<span class="risk-pill {rc_k}">{metrics["risk"]}</span>'
        f'&nbsp;&nbsp;<span style="font-size:13px;color:#6B7280;font-weight:500;">'
        f'Health Score: {metrics["health"]}/100</span>',
        unsafe_allow_html=True)
    st.markdown("<div style='margin:0.75rem 0'></div>", unsafe_allow_html=True)
    
    cls_map = {"urgent": "dec-urgent", "warning": "dec-warning", "ok": "dec-ok", "unsafe": "dec-unsafe"}
    for level, title, detail in decisions:
        st.markdown(f"""
        <div class="dec-card {cls_map.get(level, 'dec-warning')}">
          <div class="dec-title">{title}</div>
          <div class="dec-detail">{detail}</div>
        </div>""", unsafe_allow_html=True)
    
    # ==========================================================
    # SECTION 4 — EXPORT
    # ==========================================================
    st.markdown('<div class="sec-title">📥 Export</div>', unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    
    with e1:
        summary = (
            f"{lbl} | {period_label}\n"
            f"Total Alerts: {metrics['total']} | Active: {metrics['active']} | Resolved: {metrics['resolved']}\n"
            f"Severe: {metrics['severe']} | Medium: {metrics['medium']} | Anomalies: {metrics['anomalies']}\n"
            f"Health: {metrics['health']}/100 | Risk: {metrics['risk']}\n"
            f"Maintenance Cost: ${metrics['cost']:,.2f} ({metrics.get('maintenance_count', 0)} actions)"
        )
        if st.button("💾 Save to Database", use_container_width=True):
            try:
                save_report(
                    mid if mid else 0,
                    period_type,
                    metrics,
                    summary,
                    st.session_state.get("rp_start", datetime.now().strftime("%Y-%m-%d")),
                    st.session_state.get("rp_end", datetime.now().strftime("%Y-%m-%d"))
                )
                
            except Exception as e:
                st.error(f"DB error: {e}")
    
    with e2:
        if st.button("⬇ Download PDF Report", use_container_width=True):
            pdf_buf = export_pdf(lbl, period_label, metrics, decisions)
            st.download_button(
                "📄 Click to download",
                data=pdf_buf,
                file_name=f"report_{period_type}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download"
            )
    
    with e3:
        if "rp_events" in st.session_state and not st.session_state["rp_events"].empty:
            csv_buf = io.StringIO()
            st.session_state["rp_events"].to_csv(csv_buf, index=False)
            st.download_button(
                "📊 Export Alerts CSV",
                data=csv_buf.getvalue(),
                file_name=f"alerts_{period_type}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="csv_download"
            )

elif not run and "rp_metrics" not in st.session_state:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;color:#9CA3AF;">
      <div style="font-size:3.5rem;margin-bottom:1rem;">📋</div>
      <p style="font-size:1.15rem;font-weight:600;color:#374151;">
        Select a period (Daily, Weekly, or Monthly) and click Generate Report
      </p>
      <p style="font-size:13px;color:#9CA3AF;margin-top:6px;">
        Data is pulled directly from Alerts and Maintenance Dashboard 
      </p>
    </div>
    """, unsafe_allow_html=True)