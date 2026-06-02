import streamlit as st
from db_connection import get_connection
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import logging

# ----------------- Logging -----------------
logging.basicConfig(
    filename="security_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------- Authenticate User -----------------
def authenticate(username, password, user_ip="unknown"):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user is None:
        logging.warning(f"FAILED LOGIN (Unknown user): {username} | IP={user_ip}")
        cursor.close()
        conn.close()
        return None, "Invalid username or password."

    # Check if locked
    if user["locked_until"] is not None:
        if datetime.now() < user["locked_until"]:
            logging.warning(f"LOCKED ACCOUNT LOGIN ATTEMPT: {username} | IP={user_ip}")
            cursor.close()
            conn.close()
            return None, f"Account locked until {user['locked_until']}"

    # Check password hash
    if check_password_hash(user["password"], password):

        cursor.execute("""
            UPDATE users 
            SET failed_attempts = 0,
                locked_until = NULL,
                last_login = %s,
                last_ip = %s
            WHERE user_id = %s
        """, (datetime.now(), user_ip, user["user_id"]))

        conn.commit()

        logging.info(f"SUCCESS LOGIN: {username} | Role={user['role']} | IP={user_ip}")

        cursor.close()
        conn.close()
        return user, None

    # Wrong password
    failed_attempts = user["failed_attempts"] + 1

    if failed_attempts >= 5:
        locked_until = datetime.now() + timedelta(minutes=15)

        cursor.execute("""
            UPDATE users 
            SET failed_attempts = %s,
                locked_until = %s
            WHERE user_id = %s
        """, (failed_attempts, locked_until, user["user_id"]))

        conn.commit()

        logging.warning(f"ACCOUNT LOCKED: {username} after 5 failed attempts | IP={user_ip}")

        cursor.close()
        conn.close()
        return None, "Too many failed attempts. Account locked for 15 minutes."

    cursor.execute("""
        UPDATE users 
        SET failed_attempts = %s
        WHERE user_id = %s
    """, (failed_attempts, user["user_id"]))

    conn.commit()

    logging.warning(f"FAILED LOGIN: {username} | Attempts={failed_attempts} | IP={user_ip}")

    cursor.close()
    conn.close()
    return None, "Invalid username or password."


# ----------------- Logout -----------------
def logout():
    # مسح كل بيانات الجلسة
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # إعادة تعيين القيم الأساسية (اختياري لكن أفضل)
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

    # الرجوع إلى الصفحة الرئيسية
    st.switch_page("app.py")