from db_connection import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1")
    result = cursor.fetchone()

    print("Database Connected Successfully ✅")
    print(result)

    conn.close()

except Exception as e:
    print("Database Connection Failed ❌")
    print(e)