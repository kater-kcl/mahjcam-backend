import os

sql_host = ''
sql_port = 0
sql_user = ''
sql_pass = ''
sql_database = ''

jwt_sec = ''



def init_config():
    global sql_host, sql_user, sql_pass, jwt_sec, sql_port, sql_database
    sql_host = os.environ.get('SQL_HOST')
    sql_port = os.environ.get('SQL_PORT')
    sql_user = os.environ.get('SQL_USER')
    sql_pass = os.environ.get('SQL_PASS')
    sql_database = os.environ.get('SQL_DATABASE')
    jwt_sec = os.environ.get('JWT_SEC')