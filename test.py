import mysql.connector

# MySQL 데이터베이스에 연결
connection = mysql.connector.connect(
    host='192.9.0.95',
    user='root',
    password='dream',
    database='imoss'
)

if connection.is_connected():
    print("MySQL 데이터베이스에 연결되었습니다.")

    # 여기에 데이터베이스 작업을 수행할 수 있습니다.

connection.close()  # 연결 종료
