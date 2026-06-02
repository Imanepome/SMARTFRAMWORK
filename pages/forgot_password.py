import streamlit as st
import random
import time
from db_connection import get_connection
from pages.email_service import send_otp
from werkzeug.security import generate_password_hash



##
st.markdown("""
<style>
    /* hide full default navigation */
    [data-testid="stSidebarNav"] {display: none;}

    /* reduce empty space */
    section[data-testid="stSidebar"] {
        padding-top: 20px;
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


/* ───────── INPUT (Username only) ───────── */
/* أول text_input في الصفحة (username) */
div[data-testid="stTextInput"] input {
    border: 2px solid #F4A261 !important;  /* برتقالي هادئ */
    border-radius: 10px !important;
    padding: 10px !important;
    transition: 0.3s ease;
}

/* عند الضغط */
div[data-testid="stTextInput"] input:focus {
    border: 2px solid #E76F51 !important;
    box-shadow: 0 0 0 2px rgba(244, 162, 97, 0.25);
}


/* ───────── BUTTONS (Send OTP + others) ───────── */
div.stButton > button {
    background: #4DA3FF !important;   /* soft blue */
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    transition: 0.3s ease;
    font-weight: 600;
}

div.stButton > button:hover {
    background: #2F8CFF !important;
    transform: translateY(-1px);
}

</style>
""", unsafe_allow_html=True)
##
##
import streamlit as st
from ui.sidebar import render_sidebar
from datetime import datetime

render_sidebar(st.session_state.role)


##
now_txt = datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">
        🔐 Forgot Password
        <span class="live-pill"><span class="live-dot"></span>Live</span>
        <span class="header-datetime">{now_txt}</span>
    </div>
    
  </div>
</div>
""", unsafe_allow_html=True)


OTP_EXPIRY_SECONDS = 300  # 5 minutes
MAX_OTP_ATTEMPTS = 3

username = st.text_input(" Enter your username")

if username:

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        st.error("User not found ❌")

    else:
        email = user.get("email")

        if not email:
            st.error("No email registered for this user ❌")

        else:
            st.success(f"OTP will be sent to: {email}")

            # init session variables
            if "otp" not in st.session_state:
                st.session_state.otp = None
            if "otp_time" not in st.session_state:
                st.session_state.otp_time = None
            if "otp_attempts" not in st.session_state:
                st.session_state.otp_attempts = 0
            if "otp_verified" not in st.session_state:
                st.session_state.otp_verified = False

            # Send OTP button
            if st.button("📩 Send OTP"):
                st.session_state.otp = str(random.randint(100000, 999999))
                st.session_state.otp_time = time.time()
                st.session_state.otp_attempts = 0
                st.session_state.otp_verified = False

                send_otp(email, st.session_state.otp)
                st.success("OTP sent successfully ✅ (Valid for 5 minutes)")

                

            # OTP input
            otp_input = st.text_input("🔢 Enter OTP")

            # Check expiry
            if st.session_state.otp and st.session_state.otp_time:
                if time.time() - st.session_state.otp_time > OTP_EXPIRY_SECONDS:
                    st.error("OTP expired ❌ Please request a new OTP.")
                    st.session_state.otp = None
                    st.session_state.otp_time = None

            # Verify OTP
            if otp_input and st.session_state.otp:

                if st.session_state.otp_attempts >= MAX_OTP_ATTEMPTS:
                    st.error("Too many OTP attempts ❌ Please request a new OTP.")

                else:
                    if otp_input == st.session_state.otp:
                        st.success("OTP Verified ✔")
                        st.session_state.otp_verified = True
                    else:
                        st.session_state.otp_attempts += 1
                        remaining = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts
                        st.error(f"Invalid OTP ❌ Attempts left: {remaining}")

            # Change password (only if verified)
            if st.session_state.otp_verified:
                new_password = st.text_input("🔑 New Password", type="password")

                if st.button("✅ Update Password"):
                    if len(new_password) < 8:
                        st.error("Password must be at least 8 characters ❌")
                    else:
                        conn = get_connection()
                        cursor = conn.cursor()

                        hashed = generate_password_hash(new_password, method="scrypt")

                        cursor.execute("""
                            UPDATE users SET password=%s WHERE username=%s
                        """, (hashed, username))

                        conn.commit()
                        cursor.close()
                        conn.close()

                        st.success("Password updated successfully 🔐")

                        # reset otp system
                        st.session_state.otp = None
                        st.session_state.otp_time = None
                        st.session_state.otp_attempts = 0
                        st.session_state.otp_verified = False