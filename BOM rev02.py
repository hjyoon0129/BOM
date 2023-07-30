import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import Listbox, Scrollbar, Button, IntVar, Checkbutton, Entry, Text

# SQLite 데이터베이스 연결과 테이블 목록 가져오기
def get_excel_tables(search_keyword=None):
    conn = sqlite3.connect('data.db')  # 데이터베이스 파일명을 적절히 수정해주세요
    cursor = conn.cursor()

    # SQLite 데이터베이스에서 테이블 목록 가져오기
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]

    conn.close()

    # 검색 키워드가 있다면 해당 키워드가 포함된 테이블만 반환
    if search_keyword:
        table_names = [name for name in table_names if search_keyword.lower() in name.lower()]

    return table_names

# 테이블 리스트를 업데이트하는 함수
def update_table_list():
    search_keyword = search_entry.get()
    tables = get_excel_tables(search_keyword)

    listbox.delete(0, 'end')
    for table in tables:
        listbox.insert('end', table)

# tkinter 창 생성
root = tk.Tk()
root.title("Excel Table Viewer")
root.geometry("1000x1000")

# 검색 창 생성
search_label = tk.Label(root, text="검색:")
search_label.pack(side='top', padx=10, pady=5)

search_entry = Entry(root, width=30)
search_entry.pack(side='top', padx=10)

# 검색 버튼 생성
search_button = Button(root, text="검색", command=update_table_list)
search_button.pack(side='top', pady=5)

# 리스트박스 생성
listbox = Listbox(root, selectmode='single', width=30)
listbox.pack(side='left', padx=10, pady=10)

# 리스트박스 스크롤바 생성
scrollbar = Scrollbar(root, command=listbox.yview)
scrollbar.pack(side='left', fill='y')

# 리스트박스에 스크롤바 설정
listbox.config(yscrollcommand=scrollbar.set)

# SQLite 데이터베이스에 있는 엑셀 테이블 목록 가져오기
tables = get_excel_tables()

# 리스트박스에 테이블 목록 추가
for table in tables:
    listbox.insert('end', table)

# 선택된 테이블 출력하기

# 데이터 표시를 위한 Text 위젯 생성
text_widget = Text(root, wrap='word')
text_widget.pack(pady=10)

# 선택된 테이블을 데이터 표시 위젯에 표시하기
def show_selected_table():
    selected_index = listbox.curselection()
    if selected_index:
        selected_table = listbox.get(selected_index)
        conn = sqlite3.connect('data.db')  # 데이터베이스 파일명을 적절히 수정해주세요
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
        conn.close()

        # DataFrame을 문자열로 변환하여 Text 위젯에 표시
        data_str = df.to_string(index=False)  # 인덱스를 표시하지 않도록 설정
        text_widget.delete(1.0, 'end')  # 기존 데이터 삭제
        text_widget.insert('end', data_str)

# 테이블 보기 버튼
btn_show_table = Button(root, text="테이블 보기", command=show_selected_table)
btn_show_table.pack()

# 체크박스 선택 여부를 저장할 변수
selected_check = IntVar()

# 체크박스 생성
check_show_table = Checkbutton(root, text="선택한 테이블 표시", variable=selected_check)
check_show_table.pack()

root.mainloop()
