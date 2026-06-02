import streamlit as st
from auth import logout


def render_sidebar(role=None):

    # ✅ FORCE SIDEBAR WHITE ALWAYS (LOGIN + ADMIN PANEL + ALL PAGES)
    st.markdown("""
    <style>
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
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] * {
        color: #111 !important;
    }

    /* remove any overlay background or image */
    section[data-testid="stSidebar"]::before,
    section[data-testid="stSidebar"]::after {
        display: none !important;
    }

    /* hide sidebar nav if it appears */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
                
/* ─────────────────────────────
   SIDEBAR FULL HEIGHT NO SCROLL
───────────────────────────── */



/* جعل المحتوى يأخذ كامل الارتفاع */
section[data-testid="stSidebar"] .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0rem !important;
}


/* ─────────────────────────────
   NAVIGATION HOVER BLUE
───────────────────────────── */

/* hover على page_link */
[data-testid="stSidebarNav"] a:hover,
section[data-testid="stSidebar"] a:hover {
    background-color: #dbeafe !important; /* أزرق فاتح */
    color: #1d4ed8 !important;
    border-radius: 10px;
    transition: 0.2s ease-in-out;
}

/* العنصر الحالي */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #bfdbfe !important;
    color: #1d4ed8 !important;
    border-radius: 10px;
}

/* hover للنص */
section[data-testid="stSidebar"] a:hover span {
    color: #1d4ed8 !important;
}
                #

                button[data-testid="baseButton-secondary"][key="logout_btn"] {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

button[data-testid="baseButton-secondary"][key="logout_btn"]:hover {
    background-color: #1d4ed8 !important;
}
 #
                button[kind="secondary"][data-testid="baseButton-secondary"] {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    width: 100% !important;
    padding: 10px !important;
}

button[kind="secondary"][data-testid="baseButton-secondary"]:hover {
    background-color: #3B82F6 !important;
    color: white !important;
}
                #
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        st.markdown("""
        <style>
        section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
        }

        section[data-testid="stSidebar"] .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        }
        </style>
        """, unsafe_allow_html=True)

        role_title = "👤 User Panel"

        if role == "admin":
         role_title = "🛡 Admin Control Panel"

        elif role == "faults_manager":
         role_title = "⚠ Fault Prediction Panel"

        elif role == "turbine_manager":
         role_title = "📈 Anomaly Detection Panel"

        elif role == "maintenance":
         role_title = "🛠 Maintenance Panel"
        
        st.markdown(f"""
        <div style="
        position: relative;
        top: -55px;
        margin-bottom: -35px;
        padding:14px;
        background:#eff6ff;
        border:1px solid #bfdbfe;
        border-radius:12px;
        text-align:center;
        font-weight:700;
        font-size:17px;
        color:#1d4ed8;
    ">
        {role_title}
    </div>
    """, unsafe_allow_html=True)


        st.markdown("""
        <div style="
        padding:10px;
        font-size:12px;
        color:#1b5e20;
        border:2px solid #00e676;
        border-radius:10px;
        background:white;
        box-shadow: 0 0 12px rgba(0, 230, 118, 0.25);
         ">
        🟢 System Online<br>
        🔒 Secure Access Enabled
       </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="
            margin-top:15px;
            padding:10px;
            background:#f5f5f5;
            border:1px solid #e0e0e0;
            border-radius:10px;
            text-align:center;
            font-weight:600;
            color:#111;
        ">
            Role: {role.upper()}
        </div>
        """, unsafe_allow_html=True)

        

        st.markdown("<h3 style='color:#111;'>Navigation</h3>", unsafe_allow_html=True)
        if role == "admin":
            st.page_link("pages/report.py", label="📊 Report")
            
            st.page_link("pages/adminpanel.py", label="➕ Add Workers")
            st.page_link("pages/forgot_password.py", label="🔐 Change Password")
            st.page_link("pages/Alerts.py", label="🔔 Alerts")
            st.page_link("pages/maintenance.py", label="🛠️ Maintenance")
            st.page_link("pages/Predictor.py", label="⚠️ Fault Prediction")
            st.page_link("pages/turbine.py", label="📈 Anomaly Detection")

        elif role == "faults_manager":
            st.page_link("pages/Predictor.py", label="⚠️ Fault Prediction")
            st.page_link("pages/Alerts.py", label="🔔 Alerts")
            st.page_link("pages/report.py", label="📊 Report")
            st.page_link("pages/forgot_password.py", label="🔐 Change Password")
            
            

        elif role == "turbine_manager":
            st.page_link("pages/turbine.py", label="📈 Anomaly Detection")
            st.page_link("pages/Alerts.py", label="🔔 Alerts")
            st.page_link("pages/report.py", label="📊 Report")
            st.page_link("pages/forgot_password.py", label="🔐 Change Password")
            
    
            

        elif role == "maintenance":
            st.page_link("pages/Alerts.py", label="🔔 Alerts")
            st.page_link("pages/maintenance.py", label="🛠️ Maintenance")
            st.page_link("pages/report.py", label="📊 Report")

      
       

         
        if st.button(" Logout", key="logout_btn"):
         logout()
        