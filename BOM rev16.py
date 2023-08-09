import pandas as pd
import sqlite3
import os
from tkinter import Tk, Button, Listbox, END, filedialog, messagebox
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.font_manager import FontProperties

# 폰트 경로를 설정합니다.
font_path = r"C:\Users\SAMSUNG\AppData\Local\Microsoft\Windows\Fonts\현대하모니 M.ttf"

# Matplotlib의 폰트 매니저에 폰트 경로를 추가합니다.
plt.rcParams['font.family'] = FontProperties(fname=font_path).get_name()

def close_event():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        plt.close()  # 메타플롯립 창을 닫음
        root.destroy()  # Tkinter 창 종료

# tkinter 창 생성
root = Tk()
root.title("CSV Table Viewer")
root.geometry("1300x800")

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
    list_file.delete(0, tk.END)  # 리스트박스 초기화

    if keyword:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", ('%'+keyword+'%',))
    else:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]

    for table_name in table_names:
        list_file.insert(tk.END, table_name)

# 검색 기능 구현
search_frame = tk.Frame(root)
search_frame.pack(side=tk.TOP, padx=1, pady=1, anchor="w")

search_label = tk.Label(search_frame, text="Search:")
search_label.pack(side=tk.LEFT,padx=10, pady=20)

search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=10, pady=20)

search_button = tk.Button(search_frame, text="Search", command=search_table)
search_button.pack(side=tk.LEFT, pady=15)


# 버튼들을 담을 Frame 생성
buttons_frame = tk.Frame(root)
buttons_frame.pack(side=tk.TOP,anchor="w", padx=10, pady=10)

# 버튼들을 담을 Frame 생성
button_frame1 = tk.Frame(root)
button_frame1.pack(side=tk.RIGHT, anchor='ne', padx=5)

# 그래프를 출력할 프레임
graph_frame = tk.Frame(button_frame1)
graph_frame.pack(side=tk.TOP)

# CSV 파일 선택 버튼
csv_button = Button(buttons_frame, text="Select CSV File", command=select_csv_files)
csv_button.pack(side=tk.LEFT,anchor="ne")

# CSV 파일 저장 버튼
save_button = Button(buttons_frame, text="Save CSV to Database", command=save_csv_to_database)
save_button.pack(side=tk.LEFT,anchor="ne")

# 삭제 버튼
delete_button = Button(buttons_frame, text="Delete Selected Table", command=delete_selected_table)
delete_button.pack(side=tk.LEFT,anchor="ne")


#메인 리스트 박스
# 리스트박스에 데이터베이스에 저장된 테이블 이름 추가
list_file = tk.Listbox(root, width=55, height=10)
list_file.pack(side=tk.TOP, anchor="w")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()
table_names = [name[0] for name in table_names]
for table_name in table_names:
    list_file.insert(END, table_name)


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

# 버튼들을 담을 Frame 생성
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, anchor='w', padx=10, pady=10)

add_button = tk.Button(button_frame, text="Add to Selected", command=move_to_selected)
add_button.pack(side=tk.LEFT)
remove_button = tk.Button(button_frame, text="Remove from Selected", command=remove_from_selected)
remove_button.pack(side=tk.LEFT)


# overlap listbox
# 리스트박스2: 선택된 항목들을 표시하는 리스트박스
selected_list = Listbox(root, width=55, height=10)
selected_list.pack(side=tk.TOP,anchor="w")

def overlap_graphs():
    selected_columns = selected_list.get(0, tk.END)
    if len(selected_columns) == 0:
        return

    connection = sqlite3.connect(db_file)
    plt.clf()  # 기존 그래프 초기화

    for col in selected_columns:
        cursor.execute(f"SELECT * FROM {col}")
        df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

        if 'Frequency' not in df.columns:
            connection.close()
            return

        plt.semilogx(df['Frequency'], df.iloc[:, 1:], label=col)

    plt.xlabel("Frequency")
    plt.ylabel("Value")
    plt.title("Overlapping Graphs")
    plt.grid(True)
    plt.legend()
    plt.xscale('log')
    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().pack_forget()

    graph_frame.canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_frame)
    graph_frame.canvas.draw()
    graph_frame.canvas.get_tk_widget().pack()

    connection.close()

# 겹치기 버튼 생성
overlap_button = tk.Button(button_frame, text="Overlap Graphs", command=overlap_graphs)
overlap_button.pack(side=tk.LEFT)


# 그래프를 그리는 함수
def plot_graph(df, title, *args):
    global ax_hline, ax_vline, text_handles, legend_names, graph_type  # 전역 변수로 선언

    # 그래프 타입을 전역 변수로 가져옴
    graph_type = 'Line'

    fig, ax = plt.subplots(figsize=(8, 6))  # fig 객체도 생성해야 함

    legend_names = []
    colors = ['k', 'r', 'b', 'g', 'm', 'y', 'k']  # 색상 리스트 생성
    i = 0  # 색상 인덱스

    if graph_type == 'Line':
        for col in df.columns[1:]:
            color = colors[i]
            if "_SPL0" in col:
                ax.plot(df['Frequency'], df[col], *args, label=col, color=color)
                legend_names.append(col)
                i = (i + 1) % len(colors)
            elif "_Imp" in col:
                # _SPL0와 동일한 칼라를 사용
                for l in legend_names:
                    if "_SPL0" in l and l.split("_SPL0")[0] == col.split("_Imp")[0]:
                        color = ax.lines[legend_names.index(l)].get_color()
                        break
                ax.plot(df['Frequency'], df[col], *args, label=col, color=color)
                legend_names.append(col)
                i = (i + 1) % len(colors)
            else:
                ax.plot(df['Frequency'], df[col], *args, label=col, color=color)
                legend_names.append(col)
                i = (i + 1) % len(colors)

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

    # 범례의 imp가 나타나도록 수정
    handles, labels = ax.get_legend_handles_labels()
    new_handles = []
    new_labels = []
    ax.legend(handles=new_handles + ax.get_lines(), labels=new_labels + legend_names, loc='best')
    # ax_hline 초기화 (요게 없으면 아래 on_move 인식 못함)
    ax_hline = ax.axhline(y=0, color='k', linewidth=1, linestyle='--')
    ax_vline = ax.axvline(x=0, color='k', linewidth=1, linestyle='--')

    # 마우스 이동 시 호출되는 함수를 정의합니다.
    def on_move(event):
        global ax_hline, ax_vline, text_handles, legend_names  # 전역 변수로 선언
        if event.inaxes:
            x, y = event.xdata, event.ydata
            # 수평선 위치 업데이트
            ax_hline.set_ydata(y)
            ax_vline.set_xdata(x)  # 수직선 위치 업데이트
            for handle in text_handles:
                handle.remove()
            text_handles = []  # 텍스트 핸들 초기화

            if graph_type == 'Line':
                for col in y_cols:
                    # 해당 열에서의 x, y 좌표 인덱스 계산
                    idx = np.abs(data[x_col] - x).argmin()
                    x_pos, y_pos = data[x_col][idx], data[col][idx]
                    # 텍스트 위치 계산
                    x_pos_text = '{:.6g}'.format(x_pos)
                    y_pos_text = '{:.6g}'.format(y_pos)
                    # 텍스트 그리기
                    text = f'{col}: ({x_pos_text}, {y_pos_text})'
                    handle = plt.text(0.01, 0.95 - (0.05 * (y_cols.index(col))), text, fontsize=10,
                                      transform=fig.transFigure, ha='left')
                    text_handles.append(handle)

    fig.canvas.mpl_connect('motion_notify_event', on_move)

    # 그래프 오른쪽으로 15% 이동하기 (여백조절하기)
    fig.subplots_adjust(left=0.2, right=0.98)

    text_handles = []  # 전역 변수로 선언

def reset_overlapping_graphs():
    plt.clf()  # 그래프 초기화

    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().pack_forget()  # 기존 그래프 제거

# 오버랩 그래프 리셋 버튼 생성
reset_overlap_button = tk.Button(button_frame, text="Reset", command=reset_overlapping_graphs)
reset_overlap_button.pack(side=tk.LEFT)


def close_graph():
    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().destroy()
        delattr(graph_frame, 'canvas')
    if hasattr(graph_frame, 'close_button'):
        graph_frame.close_button.destroy()
        delattr(graph_frame, 'close_button')

# 리스트박스가 변경되었을 때 show_table_contents 함수를 호출하도록 바인딩
list_file.bind('<<ListboxSelect>>', show_table_contents)

def close_graph():
    plt.close()  # 그래프 창 닫기

# tkinter 창이 닫힐 때 on_closing 함수 호출
root.protocol("WM_DELETE_WINDOW", close_event)

root.mainloop()