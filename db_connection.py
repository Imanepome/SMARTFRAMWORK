import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # إذا عندك password ضعها هنا
        database="smartgrid_db"
    )