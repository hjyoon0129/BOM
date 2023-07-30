import tkinter as tk
from tkinter import filedialog
from tkinter import Listbox, END
import os
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Matplotlib 폰트 설정 (예시로 나눔고딕 폰트를 사용합니다.)
plt.rcParams["font.family"] = "NanumGothic"

# Tkinter 창 생성
root = tk.Tk()
root.title("BOM Data Viewer")
root.geometry("800x600")

# 데이터베이스 연결
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# 삭제된 테이블 목록 불러오기
deleted_tables_file = 'deleted_tables.txt'
if os.path.exists(deleted_tables_file):
    with open(deleted_tables_file, 'r') as file:
        deleted_tables = file.read().splitlines()
else:
    deleted_tables = []

# 파일 불러오기 함수
def open_files():
    global csv_filenames
    csv_filenames = filedialog.askopenfilenames(initialdir=".", title="Select CSV files",
                                                filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))

    if csv_filenames:
        save_csv_to_database()

# 데이터베이스에 CSV 파일을 저장하는 함수
def save_csv_to_database():
    global deleted_tables
    for filename in csv_filenames:
        # 1~4번째 라인을 스킵하고 5번째 라인부터 데이터를 읽어들임
        df = pd.read_csv(filename, encoding='cp949', skiprows=4, header=0)
        # 각 csv파일중 원하는 행 추출
        df = df.iloc[:, [0, 1, 2]]
        # 파일 이름을 가져와서 열 이름 변경
        spl0_col_name = os.path.basename(filename) + "_SPL0"
        imp_col_name = os.path.basename(filename) + "_Imp"
        df.columns = ["Frequency", spl0_col_name, imp_col_name]

        # 파일 이름에서 확장자를 제거한 부분으로 테이블 이름 생성
        table_name = os.path.splitext(os.path.basename(filename))[0]
        # 테이블 이름에 있는 특수 문자를 '_' (밑줄)로 치환
        sanitized_table_name = re.sub(r"[^\w]", "_", table_name)

        df.to_csv(os.path.join(data_folder, os.path.basename(filename)), index=False, encoding='cp949')
        df.to_sql(sanitized_table_name, connection, if_exists='replace', index=False)

        if sanitized_table_name in deleted_tables:
            deleted_tables.remove(sanitized_table_name)

    # 리스트박스에 데이터베이스에 저장된 테이블 이름 추가
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]

    # 이전에 삭제한 테이블은 목록에 추가하지 않음
    table_names = [name for name in table_names if name not in deleted_tables]

    list_file.delete(0, END)
    for table_name in table_names:
        list_file.insert(END, table_name)

# 그래프를 그리는 함수
def plot_graph(df, title, line_width=1, line_style='-'):
    # 'Frequency' 열이 데이터프레임에 존재하는지 확인
    if 'Frequency' not in df.columns:
        print("'Frequency' column not found in the DataFrame.")
        return

    # 그래프 그리기
    plt.figure(figsize=(8, 6))
    for col in df.columns[1:]:
        plt.semilogx(df['Frequency'], df[col], linestyle=line_style, linewidth=line_width, label=col)
    plt.xlabel("Frequency")
    plt.ylabel("Value")
    plt.title(title)
    plt.grid(True)
    plt.legend()

    # 그래프를 tkinter 창에 출력
    if hasattr(root, 'canvas'):
        root.canvas.get_tk_widget().pack_forget()  # 기존 그래프 제거
    root.canvas = FigureCanvasTkAgg(plt.gcf(), master=root)
    root.canvas.draw()
    root.canvas.get_tk_widget().pack()

# 삭제 버튼
def delete_selected_table():
    selected_table_index = list_file.curselection()
    if selected_table_index:
        selected_table_index = selected_table_index[0]
        selected_table = list_file.get(selected_table_index)
        sanitized_table = re.sub(r"[^\w]", "_", selected_table)

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        try:
            cursor.execute(f"DROP TABLE IF EXISTS {sanitized_table}")
            connection.commit()  # 변경 사항을 데이터베이스에 반영
            list_file.delete(selected_table_index)  # 리스트박스에서도 삭제

            # 삭제한 테이블 이름을 리스트와 데이터베이스에서 모두 제거
            deleted_tables.append(selected_table)
            with open(deleted_tables_file, 'w') as file:
                file.write("\n".join(deleted_tables))
        except sqlite3.Error as e:
            print("Error while deleting table:", e)
        finally:
            connection.close()


# 테이블 선택 시 내용 출력
def show_table_contents(event):
    selected_table = list_file.get(list_file.curselection())
    if selected_table:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM {}".format(selected_table))
        df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

        # 그래프 그리기
        plot_graph(df, selected_table)


# 검색 기능 구현
search_label = tk.Label(root, text="Search:")
search_label.pack(pady=5)

search_entry = tk.Entry(root)
search_entry.pack(pady=5)

def search_table():
    keyword = search_entry.get()
    if keyword:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", ('%'+keyword+'%',))
        table_names = cursor.fetchall()
        table_names = [name[0] for name in table_names]
        list_file.delete(0, END)
        for table_name in table_names:
            list_file.insert(END, table_name)
    else:
        # 검색어가 비어있으면 모든 테이블을 보여줌
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = cursor.fetchall()
        table_names = [name[0] for name in table_names]
        list_file.delete(0, END)
        for table_name in table_names:
            list_file.insert(END, table_name)

search_button = tk.Button(root, text="Search", command=search_table)
search_button.pack(pady=5)

# 리스트박스에 데이터베이스에 저장된 테이블 이름 추가
list_file = Listbox(root, width=50, height=10)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()
table_names = [name[0] for name in table_names]
for table_name in table_names:
    list_file.insert(END, table_name)
list_file.pack()

# 체크박스 클릭 이벤트 함수
def update_graph():
    selected_indices = [i for i, var in enumerate(check_vars) if var.get() == 1]
    if selected_indices:
        selected_columns = [table_names[index] for index in selected_indices]
        connection = sqlite3.connect('data.db')
        selected_df = pd.DataFrame()
        for col in selected_columns:
            cursor.execute(f"SELECT * FROM {col}")
            df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
            selected_df = pd.concat([selected_df, df.iloc[:, 1:]], axis=1)
        connection.close()

        # 그래프 그리기 전에 기존 그래프 제거
        plt.clf()
        plot_graph(selected_df, "Graph Title", line_width=2, line_style='-')
        root.canvas.draw()

# 체크박스 변수 리스트 생성
check_vars = [tk.IntVar() for _ in range(list_file.size())]

# 리스트박스 내에 체크박스 추가
for i, col in enumerate(table_names):
    check_button = tk.Checkbutton(root, text=col, variable=check_vars[i], command=update_graph)
    check_button.pack(anchor=tk.W)
    check_button.deselect()  # 초기에 선택 해제 상태로 설정

# 초기 그래프 그리기
df = pd.DataFrame()  # 초기 그래프를 빈 DataFrame으로 설정
plot_graph(df, "Graph Title")

# 리스트박스의 테이블 선택 이벤트에 그래프 업데이트 함수 연결
list_file.bind("<<ListboxSelect>>", show_table_contents)

root.mainloop()
