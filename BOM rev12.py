import pandas as pd
import sqlite3
import os
from tkinter import Tk, Button, Listbox, END, filedialog
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk

# tkinter 창 생성
root = Tk()
root.title("CSV Table Viewer")
root.geometry("1000x800")

# 데이터폴더 경로
data_folder = "data"

# 삭제한 테이블 이름들을 저장할 파일 경로
deleted_tables_file = "deleted_tables.txt"

# 데이터폴더가 없을 경우 생성
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# 데이터베이스 연결
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# 이전에 삭제한 테이블 이름을 저장할 리스트
deleted_tables = []

def sanitize_column_name(name):
    # Replace any non-word characters (except comma, parentheses, and underscore) with underscores
    sanitized_name = re.sub(r"[^\w,()]", "_", name)
    return sanitized_name

# CSV 파일을 선택하는 함수
def select_csv_files():
    global csv_filenames
    csv_filenames = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    csv_button.config(text="Selected: {} file(s)".format(len(csv_filenames)))
    # 선택한 파일 목록 표시
    list_file.delete(0, END)
    for file in csv_filenames:
        list_file.insert(END, os.path.basename(file))


# 데이터베이스에 CSV 파일을 저장하는 함수
def save_csv_to_database():
    global deleted_tables
    connection = sqlite3.connect('data.db')
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

    connection.close()


# Matplotlib 폰트 설정 (예시로 나눔고딕 폰트를 사용합니다.)
plt.rcParams["font.family"] = "NanumGothic"

# 데이터베이스 파일 이름
db_file = "data.db"

# 삭제 버튼
def delete_selected_table():
    selected_table_index = list_file.curselection()
    if selected_table_index:
        selected_table_index = selected_table_index[0]
        selected_table = list_file.get(selected_table_index)
        sanitized_table = sanitize_column_name(selected_table)

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
        sanitized_table = sanitize_column_name(selected_table)

        try:
            cursor.execute("SELECT * FROM {}".format(sanitized_table))
            df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
            print(df)

            # 그래프 그리기
            plot_graph(df, selected_table)
        except sqlite3.Error as e:
            print("Error while fetching data from table:", e)
        finally:
            connection.close()

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
            list_file.pack(side=tk.LEFT)
# 검색 기능 구현
search_frame = tk.Frame(root)
search_frame.pack(side=tk.TOP, anchor='w', padx=10, pady=10)

search_label = tk.Label(search_frame, text="Search:")
search_label.pack(side=tk.LEFT, anchor='ne', padx=10, pady=20)

search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, anchor='ne', padx=10, pady=20)

search_button = tk.Button(search_frame, text="Search", command=search_table)
search_button.pack(side=tk.RIGHT, anchor='ne', pady=15)

# 버튼들을 담을 Frame 생성
buttons_frame = tk.Frame(root)
buttons_frame.pack(side=tk.TOP, anchor='w', padx=10, pady=10)

# CSV 파일 선택 버튼
csv_button = Button(buttons_frame, text="Select CSV File", command=select_csv_files)
csv_button.pack(side=tk.LEFT, anchor='ne')

# CSV 파일 저장 버튼
save_button = Button(buttons_frame, text="Save CSV to Database", command=save_csv_to_database)
save_button.pack(side=tk.LEFT, anchor='ne')

# 삭제 버튼
delete_button = Button(buttons_frame, text="Delete Selected Table", command=delete_selected_table)
delete_button.pack(side=tk.LEFT, anchor='ne')

#메인 리스트 박스
# 리스트박스에 데이터베이스에 저장된 테이블 이름 추가
list_file = tk.Listbox(root, width=50, height=10)
list_file.pack(side=tk.LEFT, padx=5, pady=10, anchor='ne')

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()
table_names = [name[0] for name in table_names]
for table_name in table_names:
    list_file.insert(END, table_name)

# 버튼들 Frame을 리스트 박스 아래에 배치
buttons_frame.pack(side=tk.TOP, anchor='w', padx=10, pady=1)

# 리스트박스1에서 항목을 선택하면 리스트박스2로 옮기는 함수
def move_to_selected():
    selected_indices = list_file.curselection()
    for index in selected_indices:
        selected_list.insert(END, list_file.get(index))

# 리스트박스1에서 항목을 제거하는 함수
def remove_from_selected():
    selected_indices = selected_list.curselection()
    for index in selected_indices:
        selected_list.delete(index)

add_button = tk.Button(buttons_frame, text="Add to Selected", command=move_to_selected)
add_button.pack(side=tk.LEFT,anchor='ne')
remove_button = tk.Button(buttons_frame, text="Remove from Selected", command=remove_from_selected)
remove_button.pack(side=tk.LEFT,anchor='ne')


# overlap listbox
# 리스트박스2: 선택된 항목들을 표시하는 리스트박스
selected_list = Listbox(root, width=50, height=10)
selected_list.pack(side=tk.LEFT, anchor='ne', padx=5, pady=10)

# 버튼들을 담을 Frame 생성
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

# 그래프를 출력할 프레임
graph_frame = tk.Frame(button_frame)
graph_frame.pack(side=tk.TOP,anchor='ne',padx=1)


def update_graph():
    selected_columns = selected_list.get(0, tk.END)  # 선택된 항목들 가져오기
    if not selected_columns:
        print("No selected columns.")
        return

    connection = sqlite3.connect(db_file)
    selected_df = pd.DataFrame()  # 빈 데이터프레임 생성
    for col in selected_columns:
        cursor.execute(f"SELECT * FROM {col}")
        df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

        # 'Frequency' 열이 없는 경우 처리
        if 'Frequency' not in df.columns:
            print(f"'Frequency' column not found in the DataFrame for table '{col}'.")
            connection.close()
            return

        # 'Frequency' 열만 같고 나머지는 다른 열들끼리 합치기
        if selected_df.empty:
            selected_df = df
        else:
            selected_df = pd.merge(selected_df, df.iloc[:, 1:], on='Frequency', how='outer')

    connection.close()

    if not selected_df.empty:
        # 그래프 그리기 전에 기존 그래프 제거
        plt.clf()
        plot_graph(selected_df, "Graph Title", line_width=2, line_style='-')
        root.canvas.draw()
    else:
        print("Empty selected DataFrame.")

# 그래프를 그리는 함수
def plot_graph(df, title, *args):
    # 그래프 그리기
    plt.figure(figsize=(8, 6))
    for col in df.columns[1:]:
        plt.semilogx(df['Frequency'], df[col], *args, label=col)
    plt.xlabel("Frequency")
    plt.ylabel("Value")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.xscale('log')  # x축을 로그 스케일로 설정

    # 그래프를 tkinter 창에 출력
    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().pack_forget()  # 기존 그래프 제거
    graph_frame.canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_frame)
    graph_frame.canvas.draw()
    graph_frame.canvas.get_tk_widget().pack()

# 리스트박스가 변경되었을 때 show_table_contents 함수를 호출하도록 바인딩
list_file.bind('<<ListboxSelect>>', show_table_contents)

# 프로그램 종료 시 삭제한 테이블 이름을 파일에 저장
def on_closing():
    with open(deleted_tables_file, 'w') as file:
        file.write("\n".join(deleted_tables))
    root.destroy()

# tkinter 창이 닫힐 때 on_closing 함수 호출
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
