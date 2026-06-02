from db_connection import get_connection
import mysql.connector
# insert prediction 

def insert_prediction(machine_id, window_number, timestamp,fault_type, severity, type_confidence, severity_confidence):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO predictions 
    (machine_id, window_number,timestamp, fault_type,type_confidence, severity, severity_confidence)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (machine_id, window_number,timestamp, fault_type, type_confidence, severity, severity_confidence))
    conn.commit()

    cursor.close()
    conn.close()
## insert anomlies



def insert_anomaly(machine_id,timestamp, anomaly_score, is_anomaly):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO anomalies (machine_id,timestamp,anomaly_score , is_anomaly)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (machine_id,timestamp, float(anomaly_score),  int(is_anomaly)))
    conn.commit()

    cursor.close()
    conn.close()    


## insert alerts




def insert_alert(machine_id,timestamp, alert_type, message,fault_type,severity, is_anomaly, status="active"):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO alerts (machine_id,timestamp, alert_type, message,fault_type ,severity, is_anomaly, status)
    VALUES (%s, %s, %s, %s, %s, %s,%s,%s)
    """

    cursor.execute(sql, (machine_id, timestamp,alert_type, message ,fault_type, severity, int(is_anomaly), status))
    conn.commit()

    cursor.close()
    conn.close()

#maintenance

# ==============================
# FETCH ACTIVE ALERTS
# ==============================
import pandas as pd
def fetch_active_alerts(machine_id=None):
    conn = get_connection()

    if machine_id:
        query = """
        SELECT a.*
        FROM alerts a
        INNER JOIN (
            SELECT machine_id, alert_type, message, fault_type, severity, is_anomaly, status,
                   MAX(timestamp) AS max_time
            FROM alerts
            WHERE status='active' AND machine_id=%s
            GROUP BY machine_id, alert_type, message, fault_type, severity, is_anomaly, status
        ) latest
        ON a.machine_id = latest.machine_id
        AND a.alert_type = latest.alert_type
        AND a.message = latest.message
        AND (a.fault_type <=> latest.fault_type)
        AND (a.severity <=> latest.severity)
        AND a.is_anomaly = latest.is_anomaly
        AND a.status = latest.status
        AND a.timestamp = latest.max_time
        ORDER BY a.timestamp DESC
        """
        df = pd.read_sql(query, conn, params=(machine_id,))

    else:
        query = """
        SELECT a.*
        FROM alerts a
        INNER JOIN (
            SELECT machine_id, alert_type, message, fault_type, severity, is_anomaly, status,
                   MAX(timestamp) AS max_time
            FROM alerts
            WHERE status='active'
            GROUP BY machine_id, alert_type, message, fault_type, severity, is_anomaly, status
        ) latest
        ON a.machine_id = latest.machine_id
        AND a.alert_type = latest.alert_type
        AND a.message = latest.message
        AND (a.fault_type <=> latest.fault_type)
        AND (a.severity <=> latest.severity)
        AND a.is_anomaly = latest.is_anomaly
        AND a.status = latest.status
        AND a.timestamp = latest.max_time
        ORDER BY a.timestamp DESC
        """
        df = pd.read_sql(query, conn)

    conn.close()
    return df

# ==============================
# INSERT MAINTENANCE ACTION
# ==============================
def insert_maintenance_action(machine_id, alert_id, timestamp, action_type, description,
                              performed_by, part_replaced, cost, status):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO maintenance_actions
    (machine_id, alert_id, timestamp, action_type, description, performed_by, part_replaced, cost, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        machine_id, alert_id, timestamp, action_type, description,
        performed_by, part_replaced, cost, status
    ))

    conn.commit()
    cursor.close()
    conn.close()


# ==============================
# UPDATE ALERT STATUS
# ==============================
def update_alert_status_group(machine_id, alert_type, fault_type, severity, is_anomaly, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE alerts
        SET status=%s
        WHERE machine_id=%s
          AND alert_type=%s
          AND (fault_type <=> %s)
          AND (severity <=> %s)
          AND is_anomaly=%s
    """, (new_status, machine_id, alert_type, fault_type, severity, is_anomaly))

    conn.commit()
    conn.close()

# ==============================
# FETCH MAINTENANCE HISTORY
# ==============================
def fetch_maintenance_history(machine_id=None):
    conn = get_connection()

    if machine_id:
        query = """
        SELECT *
        FROM maintenance_actions
        WHERE machine_id=%s
        ORDER BY timestamp DESC
        """
        df = pd.read_sql(query, conn, params=(machine_id,))
    else:
        query = """
        SELECT *
        FROM maintenance_actions
        ORDER BY timestamp DESC
        """
        df = pd.read_sql(query, conn)

    conn.close()
    return df
#



    