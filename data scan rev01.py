import sqlite3
import tkinter as tk
from tkinter import messagebox, Listbox, Button, END

# 데이터베이스 파일 경로
db_path = 'data.db'

# Tkinter 창 생성
root = tk.Tk()
root.title("Table Deletion")

# SQLite 데이터베이스 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 데이터베이스 내의 테이블 목록 얻기
def get_table_names():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

# 테이블 목록 보여주는 Listbox
table_listbox = Listbox(root, width=30)  # 열 너비 설정
for table in get_table_names():
    table_listbox.insert(END, table)
table_listbox.pack()

# 선택한 테이블 삭제하는 함수
def delete_table():
    selected_table = table_listbox.get(table_listbox.curselection())
    if selected_table:
        if messagebox.askyesno("Delete Table", f"Do you want to delete table '{selected_table}'?"):
            cursor.execute(f"DROP TABLE IF EXISTS `{selected_table}`")
            conn.commit()
            messagebox.showinfo("Table Deleted", f"Table '{selected_table}' has been deleted.")
            refresh_table_list()

# 테이블 목록 갱신하는 함수
def refresh_table_list():
    table_listbox.delete(0, END)
    for table in get_table_names():
        table_listbox.insert(END, table)

# 삭제 버튼 생성
delete_button = Button(root, text="Delete", command=delete_table)
delete_button.pack()

# 연결 닫기 함수
def close_connection():
    conn.close()
    root.destroy()

# 창 닫을 때 연결 닫기
root.protocol("WM_DELETE_WINDOW", close_connection)

# Tkinter 창 실행
root.mainloop()
