import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import Listbox, Scrollbar, Button, IntVar, Checkbutton, Entry, Text, filedialog
import matplotlib.pyplot as plt
import os

root = tk.Tk()
root.title("Excel Table Viewer")
root.geometry("1000x1000")

# 엑셀 파일을 읽어와 SQLite에 저장하는 함수
def load_excel_to_sqlite(file_path, table_name):
    # 엑셀 파일 읽기
    df = pd.read_excel(file_path)

    # SQLite 데이터베이스 연결
    connection = sqlite3.connect('data.db')

    # 데이터프레임을 SQLite 테이블로 저장
    df.to_sql(table_name, connection, if_exists='replace', index=False)

    # 연결 종료
    connection.close()


# 엑셀 파일 경로와 테이블 이름 설정
file_path = 'your_excel_file.xlsx'  # 엑셀 파일 경로를 지정해주세요
table_name = 'excel_data'  # SQLite 테이블 이름을 지정해주세요

# SQLite에 데이터 저장
load_excel_to_sqlite(file_path, table_name)





def load_csv_to_sqlite(file_path, table_name):
    df = pd.read_csv(file_path)
    connection = sqlite3.connect('data.db')
    df.to_sql(table_name, connection, if_exists='replace', index=False)
    connection.close()
    update_table_list()

def add_file(file_format):
    filetypes = [("Excel Files", "*.xlsx;*.xls"), ("CSV Files", "*.csv")]
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        file_name = os.path.basename(file_path)
        new_file_path = os.path.join("data", file_name)

        if not os.path.exists("data"):
            os.makedirs("data")

        os.rename(file_path, new_file_path)

        if file_format == "Excel":
            load_excel_to_sqlite(new_file_path, file_name)
        elif file_format == "CSV":
            load_csv_to_sqlite(new_file_path, file_name)

def add_csv_file():
    add_file("CSV")


btn_add_csv = Button(root, text="Add CSV File", command=add_file())
btn_add_csv.pack()

def get_excel_tables(search_keyword=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]
    conn.close()

    if search_keyword:
        table_names = [name for name in table_names if search_keyword.lower() in name.lower()]

    return table_names

def update_table_list():
    search_keyword = search_entry.get()
    tables = get_excel_tables(search_keyword)

    listbox.delete(0, 'end')
    for table in tables:
        listbox.insert('end', table)

search_label = tk.Label(root, text="검색:")
search_label.pack(side='top', padx=10, pady=5)

search_entry = Entry(root, width=30)
search_entry.pack(side='top', padx=10)

search_button = Button(root, text="검색", command=update_table_list)
search_button.pack(side='top', pady=5)

listbox = Listbox(root, selectmode='single', width=30)
listbox.pack(side='left', padx=10, pady=10)

scrollbar = Scrollbar(root, command=listbox.yview)
scrollbar.pack(side='left', fill='y')

listbox.config(yscrollcommand=scrollbar.set)

tables = get_excel_tables()

for table in tables:
    listbox.insert('end', table)

text_widget = Text(root, wrap='word')
text_widget.pack(pady=10)

def show_selected_table():
    selected_index = listbox.curselection()
    if selected_index:
        selected_table = listbox.get(selected_index)
        conn = sqlite3.connect('data.db')
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
        conn.close()

        plt.figure(figsize=(8, 6))
        plt.plot(df['Frequency'], df['SPL0'], label='SPL0', marker='o')
        plt.plot(df['Frequency'], df['Imp'], label='Imp', marker='o')
        plt.xlabel('Frequency')
        plt.ylabel('Value')
        plt.title(f'{selected_table} 그래프')
        plt.legend()

        plt.tight_layout()
        plt.savefig('temp_plot.png')
        plt.close()

        img = tk.PhotoImage(file='temp_plot.png')
        label = tk.Label(root, image=img)
        label.image = img
        label.pack()

btn_show_table = Button(root, text="테이블 보기", command=show_selected_table)
btn_show_table.pack()

selected_check = IntVar()

check_show_table = Checkbutton(root, text="선택한 테이블 표시", variable=selected_check)
check_show_table.pack()

root.mainloop()
