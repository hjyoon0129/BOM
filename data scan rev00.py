import sqlite3

# SQLite 데이터베이스에 연결
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 데이터베이스 내의 테이블 목록 얻기
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()

# 테이블 목록 출력
print("Available tables:")
for table in table_names:
    print(table[0])

# 연결 닫기
conn.close()