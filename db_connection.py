import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="acela.proxy.rlwy.net",
        port=14633,
        user="root",
        password="vvvwjGTizyfJFsNENCikUZtZAIzwXflg",
        database="railway"
    )