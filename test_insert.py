from db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()

sql = """
INSERT INTO predictions (machine_id, fault_type, severity, confidence)
VALUES (%s, %s, %s, %s)
"""

values = (2, "H", "normal", 95.5)
cursor.execute(sql, values)
conn.commit()

print("Inserted Successfully ✅")

cursor.close()
conn.close()