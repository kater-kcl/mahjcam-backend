import json
from typing import Union

from numpy import number

import src.global_data.config as config
import mysql.connector
import bcrypt

sql_args: dict[str, Union[str, int]]


def init_mysql():
    global sql_args
    sql_args = {
        'host': config.sql_host,
        'port': int(config.sql_port),
        'user': config.sql_user,
        'password': config.sql_pass,
        'database': config.sql_database
    }


def register_user(username: str, password: str, e_mail: str):
    conn = mysql.connector.connect(**sql_args)
    cursor = conn.cursor()
    # Check if the username already exists
    cursor.execute("SELECT COUNT(*) FROM user_table WHERE username = %s", (username,))
    if cursor.fetchone()[0] > 0:
        return False

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert the new user into the database
    cursor.execute("INSERT INTO user_table (username, password, email) VALUES (%s, %s, %s)",
                   (username, hashed_password.decode('utf-8'), e_mail))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def login_check(username: str, password: str):
    conn = mysql.connector.connect(**sql_args)
    cursor = conn.cursor()
    # Check if the username exists
    cursor.execute("SELECT password FROM user_table WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result is None:
        return False

    # Verify the password
    hashed_password = result[0].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return True
    else:
        return False


def get_user_info(username: str):
    conn = mysql.connector.connect(**sql_args)
    cursor = conn.cursor()
    # Check if the username exists
    cursor.execute("SELECT * FROM user_table WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result is None:
        return None

    # Return user info
    user_info = {
        'uid': result[0],
        'username': result[1],
        'email': result[3],
    }
    return user_info


def append_history(user_id: str, history: str) -> int:
    global sql_args
    conn = mysql.connector.connect(**sql_args)
    cursor = conn.cursor()

    insert_sql = '''
        INSERT INTO `image_scans` (user_id, scan_data)
        VALUES (%s, %s)
    '''
    args = (user_id, history)
    cursor.execute(insert_sql, args)
    conn.commit()

    scan_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return scan_id


def update_history(scan_id: str, user_id: str, history: str) -> bool:
    global sql_args
    conn = mysql.connector.connect(**sql_args)
    cursor = conn.cursor()

    update_sql = '''
        UPDATE `image_scans`
        SET scan_data = %s
        WHERE scan_id = %s AND user_id = %s
    '''
    args = (history, scan_id, user_id)
    cursor.execute(update_sql, args)
    conn.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    conn.close()
    return affected_rows != 0


def query_user_recent_history(user_id: str, limit: int = 10) -> list[dict]:
    global sql_args
    conn = mysql.connector.connect(**sql_args)
    cursor = conn.cursor()

    select_sql = '''
        SELECT scan_id, scan_data, update_time
        FROM `image_scans`
        WHERE user_id = %s
        ORDER BY update_time DESC
        LIMIT %s
    '''
    args = (user_id, limit)
    cursor.execute(select_sql, args)

    results = cursor.fetchall()
    history_list = []
    for row in results:
        history_list.append({
            'scan_id': row[0],
            'scan_data': json.loads(row[1]),
            'update_time': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None
        })
    cursor.close()
    conn.close()
    return history_list
