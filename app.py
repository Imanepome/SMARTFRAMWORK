import streamlit as st
import socket
from auth import authenticate, logout
from ui.sidebar import render_sidebar
import base64


st.set_page_config(
    page_title="Smart Grid Secure System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)



# ---------------- BASE64 IMAGE ----------------
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def load_css():
    st.markdown("""
    <style>

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

        
        .stApp {
            background-color: white;
            
                
        }
                
html, body {
    height: 100%;
    overflow: hidden !important;
    margin: 0;
    padding: 0;
}

.stApp {
    height: 100vh !important;
    overflow: hidden !important;
}

/* فقط منع scroll في الخلفية وليس المحتوى */
[data-testid="stAppViewContainer"] {
    overflow: hidden !important;
}

/* مهم: نخلي المحتوى ياخذ مساحة طبيعية */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto !important;
    max-height: 100vh !important;
}

/* منع scroll فقط داخل الصفحة الرئيسية */
section.main {
    overflow: hidden !important;
}
                #
          /* LOGIN CONTAINER */
        .login-container {
            width: 100px;
                 
            text-align: center;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #0a0f16 !important;
            border-right: 1.5px solid #f97316 !important;
        }
        section[data-testid="stSidebar"] * {
            color:  #f97316 !important;
        }

        @keyframes spin      { to { transform: rotate(360deg);  } }
        @keyframes spinRev   { to { transform: rotate(-360deg); } }
        @keyframes floatY    { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
        @keyframes floatTilt { 0%,100%{transform:translateY(0) rotate(-15deg)} 50%{transform:translateY(-8px) rotate(-15deg)} }
        @keyframes pulse     { 0%,100%{opacity:1} 50%{opacity:.45} }
        @keyframes scanline  { 0%{top:-10%} 100%{top:110%} }

        .sidebar-hero {
            position: relative;
            height: 210px;
            overflow: hidden;
            background: #0d1520;
            border-radius: 10px;
            border: 1px solid #f9731640;
            margin-bottom: 10px;
        }
        .sidebar-hero::after {
            content: '';
            position: absolute;
            left: 0; right: 0;
            height: 60px;
            background: linear-gradient(transparent, #f9731610, transparent);
            animation: scanline 3.5s linear infinite;
            pointer-events: none;
        }
        .sidebar-hero::before {
            content: '';
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(#f9731612 1px, transparent 1px),
                linear-gradient(90deg, #f9731612 1px, transparent 1px);
            background-size: 28px 28px;
        }

        .gear-main  { position:absolute; font-size:155px; left:-72px; top:22px;   animation:spin    8s linear infinite; opacity:.88; filter:sepia(1) saturate(4) hue-rotate(5deg); user-select:none; }
        .gear-small { position:absolute; font-size:58px;  right:8px;  top:6px;    animation:spinRev 4s linear infinite; opacity:.72; filter:sepia(1) saturate(4) hue-rotate(5deg); user-select:none; }
        .gear-mid   { position:absolute; font-size:80px;  right:28px; bottom:30px; animation:spin  12s linear infinite; opacity:.55; filter:sepia(1) saturate(3) hue-rotate(5deg); user-select:none; }
        .tool-wrench{ position:absolute; font-size:40px;  right:20px; top:72px;   animation:floatTilt 3s ease-in-out infinite;    opacity:.85; filter:sepia(1) saturate(3) hue-rotate(8deg); user-select:none; }
        .tool-hammer{ position:absolute; font-size:34px;  right:52px; bottom:14px; animation:floatY 4s ease-in-out infinite 1s;  opacity:.78; filter:sepia(1) saturate(3) hue-rotate(8deg); user-select:none; }
        .tool-bolt  { position:absolute; font-size:26px;  left:92px;  bottom:10px; animation:floatY 3.5s ease-in-out infinite .5s; opacity:.72; filter:sepia(1) saturate(3) hue-rotate(5deg); user-select:none; }

        .sidebar-brand {
            background: #f97316;
            border-radius: 8px;
            padding: 10px 14px;
            text-align: center;
            margin-bottom: 12px;
        }
        .sidebar-brand .brand-title    { font-weight:700; font-size:14px; color:#fff; letter-spacing:.5px; }
        .sidebar-brand .brand-subtitle { font-size:10px; color:#fed7aa; margin-top:2px; }

        .sidebar-stats { display:flex; gap:6px; margin-bottom:14px; }
        .stat-chip {
            flex: 1;
            background: #0d1520;
            border: 1px solid #f9731630;
            border-radius: 8px;
            padding: 8px 4px;
            text-align: center;
        }
        .stat-chip .sc-val   { font-size:13px; font-weight:700; color:#f97316 !important; display:block; }
        .stat-chip .sc-label { font-size:9px;  color:#64748b  !important; display:block; margin-top:1px; }

        .nav-section-label {
            font-size: 9px;
            letter-spacing: 2px;
            color: #f97316 !important;
            text-transform: uppercase;
            margin: 14px 0 6px;
            border-left: 2px solid #f97316;
            padding-left: 8px;
        }

        /* ── Login card — أبيض ── */
        .login-card {
            background: #ffffff;
            padding: 40px 35px 35px;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            text-align: center;
        }

        /* خط برتقالي علوي */
        .login-card::before {
            content: '';
            display: block;
            height: 3px;
            background: linear-gradient(90deg, transparent, #f97316, transparent);
            border-radius: 2px;
            margin-bottom: 28px;
        }

        .main-title { font-size:32px; font-weight:800; color:#111 !important; margin-bottom:6px; }
        .subtitle   { font-size:14px; color:#64748b; margin-bottom:24px; }

      /* ALERT BLUE ONLY */
    .warning-box {
        background: #eff6ff;
        border: 1px solid #3b82f6;
        border-left: 5px solid #2563eb;
        padding: 12px;
        border-radius: 10px;
        color: #1e3a8a;
        font-size: 12px;
        margin-bottom: 15px;
    }
              
div.stButton {
    display: flex;
    justify-content: center;
    width: 100%;
}

div.stButton > button {
    width: 160% !important;   
    max-width: 420px;        
    height: 30px;
    font-size: 18px;
    font-weight: 900;
    background: #2563eb !important;
    color: white !important;
    border-radius: 12px;
    border: none;
    margin-top: 18px;
    letter-spacing: 1px;
    transition: 0.2s ease-in-out;
    display: block;
}

div.stButton > button:hover {
    background: #1d4ed8 !important;
    transform: scale(1.04);
} 
        /* ── Inputs — أبيض ── */
        .stTextInput input {
            border-radius: 8px !important;
            padding: 10px !important;
            border: 1.5px solid  #93c5fd !important;
            background-color: #f8fafc !important;
            
        }
        .stTextInput input:focus {
            border-color: #f97316 !important;
            box-shadow: 0 0 0 2px #f9731625 !important;
        }

        .footer-text {
            margin-top: 16px;
            font-size: 11px;
            color: #94a3b8;
            font-family: 'Share Tech Mono', monospace;
        }

        /* ── Dash box ── */
        .dash-box {
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            color: #111;
        }

        h1, h2, h3, h4 { color: #111 !important; }
          
       

        /* BIG LOGO - modified to stay ABOVE the warning and CENTERED */
        .login-logo-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 30px;
        }

     
        .login-logo img {
            width: 200px;
            height: 50;
             display: block; 
            
        }
        
        /* New container that keeps image ABOVE the warning box */
        .image-above-warning {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .image-above-warning .login-logo {
            margin-bottom: 25px;
        }
        .image-above-warning .warning-box {
            width: 100%;
            box-sizing: border-box;
        }
                .tagline{
    margin-top: -10px;
    margin-bottom: 18px;
    font-size: 16px;
    font-weight: 700;
    color: #f97316;
    letter-spacing: 1px;
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
}
                
  .hero-title{
    text-align:center;
    font-size: 34px;
    font-weight: 900;
    margin-top: 10px;
    margin-bottom: 6px;
    font-family: 'Rajdhani', sans-serif;
    color: #111;
}

.hero-sub{
    text-align:center;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 18px;
    font-family: 'Share Tech Mono', monospace;
}

.tag{
    padding: 7px 14px;
    border-radius: 10px;
    font-weight: 600;
    display: inline-block;
    margin: 0 4px;
    font-size: 13px; 
    letter-spacing: 0.5px;
    transition: all 0.25s ease-in-out;
}

/* ── ORANGE ── */
.tag.o{
    background:#fff4ed;
    color:#c2540a;
    border:1px solid rgba(249,115,22,.3);
    text-shadow: 0 0 6px rgba(249,115,22,0.55);
}

.tag.o:hover{
    box-shadow: 0 0 10px rgba(249,115,22,0.6);
}

/* ── BLUE ── */
.tag.b{
    background:#eff6ff;
    color:#1d4ed8;
    border:1px solid rgba(59,130,246,.3);
    text-shadow: 0 0 6px rgba(59,130,246,0.55);
}

.tag.b:hover{
    box-shadow: 0 0 10px rgba(59,130,246,0.6);
}

/* ── GREEN ── */
.tag.g{
    background:#f0fdf4;
    color:#15803d;
    border:1px solid rgba(22,163,74,.3);
    text-shadow: 0 0 6px rgba(34,197,94,0.55);
}

.tag.g:hover{
    box-shadow: 0 0 10px rgba(34,197,94,0.6);
}

/* ── TITLE ── */
.industrial-title{
    text-align: center;
    font-size: 38px; 
    font-weight: 900;
    margin-top: 10px;
    margin-bottom: 6px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 2px;
    text-transform: uppercase;
    text-shadow: 0 0 12px rgba(255,255,255,0.15);
}

/* ── SUB COLORS + GLOW ── */
.industrial-sub .o{
    color:#f97316;
    text-shadow: 0 0 8px rgba(249,115,22,0.6);
}

.industrial-sub .b{
    color:#3b82f6;
    text-shadow: 0 0 8px rgba(59,130,246,0.6);
}

.industrial-sub .g{
    color:#22c55e;
    text-shadow: 0 0 8px rgba(34,197,94,0.6);
}

.industrial-sub{
    text-align:center;
    font-size: 17px; 
    color: #64748b;
    margin-bottom: 18px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
}
                


/* نخلي كل المحتوى فوق الصورة */
section[data-testid="stSidebar"] > div {
    position: relative;
    z-index: 2;
}

/* الخلفية (الصورة) تغطي كامل الـ sidebar */
section[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    inset: 0;

    background-image: url("data:image/jpg;base64,E:\SmartGridV01\images\22.jpg");
    background-size: cover;        /* أهم شيء: تغطية كاملة */
    background-position: center;
    background-repeat: no-repeat;
    opacity: 1;   /* IMPORTANT: fully solid */
    z-index: 1;
  
}

                
    </style>
    """, unsafe_allow_html=True)


load_css()

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
section[data-testid="stSidebar"] {padding-top: 0px;}
</style>
""", unsafe_allow_html=True)


def init_session():
    if "logged_in"  not in st.session_state: st.session_state.logged_in  = False
    if "role"       not in st.session_state: st.session_state.role       = None
    if "username"   not in st.session_state: st.session_state.username   = None

init_session()


def get_user_ip():
    try:    return socket.gethostbyname(socket.gethostname())
    except: return "unknown"


def render_industrial_sidebar():
    logo_base64 = get_base64_image("images/22.jpg")

    st.markdown(f"""
    <style>
    section[data-testid="stSidebar"] {{
        position: relative;
        background-color: #fff !important;
        overflow: hidden !important;
    }}

    section[data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        inset: 0;
        background-image: url("data:image/jpg;base64,{logo_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        opacity: 0.85;
        z-index: 1;
    }}

    section[data-testid="stSidebar"] > div {{
        position: relative;
        z-index: 2;
    }}
    </style>
    """, unsafe_allow_html=True)

def login_page():
    render_industrial_sidebar()

 

    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        logo_base64 = get_base64_image("images/logo.png")

        # MODIFIED: الصورة تبقى فوق رسالة ALERT وتظهر في المنتصف
        st.markdown(f"""
        <div class="image-above-warning">
            <div class="login-logo">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo">
                
           
            """, unsafe_allow_html=True)

            # 
        st.markdown("""
           <div class="industrial-sub">
           <span class="o">PREDICT.</span>
            <span class="b">DEETECT.</span>
           <span class="g">OPTIMIZE</span>
           </div>

            <div class="industrial-sub">
           Intelligent Management System
          </div>
          """, unsafe_allow_html=True)
            #
        st.markdown("""
        <div class='warning-box'>
                🔐 ALERT: Unauthorized access attempts are monitored and logged.<br>
                ⚠️ Critical Infrastructure Security Protocol — ENABLED
            </div>
        
        """, unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            user_ip = get_user_ip()
            user, error = authenticate(username, password, user_ip)
            if error:
                st.error(error)
            else:
                st.session_state.logged_in = True
                st.session_state.username  = user["username"]
                st.session_state.role      = user["role"]
                st.rerun()

        





if st.session_state.logged_in:
    render_sidebar(st.session_state.role)
    
else:
    login_page()