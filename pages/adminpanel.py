import streamlit as st
from werkzeug.security import generate_password_hash
from datetime import datetime
from db_connection import get_connection


##



##
st.markdown("""
<style>
    /* hide full default navigation */
    [data-testid="stSidebarNav"] {display: none;}

    /* reduce empty space */
    section[data-testid="stSidebar"] {
        padding-top: 20px;
    }

    /* ── INPUT BORDER ORANGE ── */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] {
        border: 1px solid orange !important;
        border-radius: 8px !important;
    }

    .stTextInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border: 2px solid orange !important;
        box-shadow: 0 0 0 1px orange !important;
    }

    /* ── DELETE BUTTON BLUE ── */
    div.stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }

    div.stButton > button:hover {
        background-color: #1D4ED8 !important;
        color: white !important;
    }
     /* ── ADD WORKER BUTTON BLUE ── */
    div[data-testid="stForm"] button {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    }

    div[data-testid="stForm"] button:hover {
    background-color: #1D4ED8 !important;
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

    @keyframes lp {
        0%,100%{opacity:1;}
        50%{opacity:.2;}
    }
</style>
""", unsafe_allow_html=True)
##
##
import streamlit as st
from ui.sidebar import render_sidebar

render_sidebar(st.session_state.role)


##

# ---------------- Security: Admin only ----------------
def require_admin():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("Please login first.")
        st.stop()

    if st.session_state.role != "admin":
        st.error("🚫 Access denied. Admin only.")
        st.stop()

require_admin()


now_txt = datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">
        🛡️ Admin Panel - Manage Workers
        <span class="live-pill"><span class="live-dot"></span>Live</span>
        <span class="header-datetime">{now_txt}</span>
    </div>
    
  </div>
</div>
""", unsafe_allow_html=True)



# ---------------- ADD USER ----------------



with st.form("add_user_form"):
    username = st.text_input("👤 Engineer Username")
    password = st.text_input("🔐 Password", type="password")

    role = st.selectbox(
        "👥 Role",
        [ "faults_manager", "turbine_manager", "maintenance",]
    )
    email = st.text_input("📧 Email Address")

    submit = st.form_submit_button("➕ Add Worker")

    if submit:
        if username == "" or password == "" or email == "":
            st.error("❌ Fields cannot be empty.")
        elif "@" not in email or "." not in email:
            st.error("❌ Invalid email format.")
        else:
            conn = get_connection()
            cursor = conn.cursor()

            # check if username exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            exists_user = cursor.fetchone()

            # check if email exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            exists_email = cursor.fetchone()

            if exists_user:
                st.error("⚠️ Username already exists.")
            elif exists_email:
                st.error("⚠️ Email already exists.")
            else:
                hashed_password = generate_password_hash(password, method="scrypt")

                cursor.execute("""
                    INSERT INTO users (username, password, role, email, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, hashed_password, role,email, datetime.now()))

                conn.commit()
                st.success(f"✅ Worker '{username}' added successfully.")

            cursor.close()
            conn.close()

st.divider()
# ---------------- SHOW USERS ----------------
st.subheader("📋 Workers List")

conn = get_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT user_id, username, role, created_at,failed_attempts,last_login,last_ip,email FROM users ORDER BY user_id DESC")
users = cursor.fetchall()

cursor.close()
conn.close()

st.dataframe(users, use_container_width=True)

st.divider()

# ---------------- DELETE USER ----------------
st.subheader("🗑️ Delete Worker")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT user_id, username FROM users WHERE username != 'admin'")
all_users = cursor.fetchall()

cursor.close()
conn.close()

if all_users:
    user_dict = {f"{u[1]} (ID:{u[0]})": u[0] for u in all_users}

    selected = st.selectbox("Select user to delete", list(user_dict.keys()))

    if st.button("❌ Delete Worker"):
        user_id = user_dict[selected]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()

        cursor.close()
        conn.close()

        st.success("🗑️ Worker deleted successfully.")
        st.rerun()
else:
    st.info("No workers to delete.")