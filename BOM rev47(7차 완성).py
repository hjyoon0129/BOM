import time

import pandas as pd
import sqlite3
import os
from tkinter import *
from tkinter import Tk, Button, Listbox, END, filedialog, messagebox, Toplevel, Label, Entry, ttk, DISABLED
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.font_manager import FontProperties
import numpy as np
import multiprocessing


# Matplotlib의 폰트 매니저에 기본 폰트를 지정합니다.
plt.rcParams['font.family'] = 'Arial'

def close_event():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        plt.close('all')
        root.destroy()  # Tkinter 창 종료
        # 메타플롯립의 모든 그래프 내용 삭제

# tkinter 창 생성
root = Tk()
root.title("SPL GRAPH Viewer _ MADE BY [A]")
# root.geometry("1500x700")
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", close_event)  # 창이 닫힐 때 close_event 호출
root.option_add("*Font", "나눔고딕 8")

# 데이터폴더 경로
data_folder = "data"

# 삭제한 테이블 이름들을 저장할 파일 경로
deleted_tables_file = "deleted_tables.txt"

# 데이터폴더가 없을 경우 생성
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# 데이터베이스 연결
connection = sqlite3.connect('data.db', isolation_level=None)
cursor = connection.cursor()
cursor.execute('PRAGMA journal_mode=WAL;')


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
    # 텍스트 위젯을 활성화하고 배경색을 기본 색상으로 변경
    text_widget.config(state='normal', bg='white')
    # 텍스트 위젯 내용 초기화
    text_widget.delete("1.0", END)

# 전역 변수
selected_table = ""
# 전역 범위에서 sanitized_table 변수를 정의합니다.
sanitized_table = ""

def save_csv_to_database():
    global deleted_tables
    global selected_table

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()  # 커서를 만듭니다

    # 텍스트 위젯을 비활성화하고 배경색을 회색으로 변경
    text_widget.config(state='disabled', bg='light gray')

    for filename in csv_filenames:
        # 1~4번째 라인을 스킵하고 5번째 라인부터 데이터를 읽어들임
        df = pd.read_csv(filename, encoding='cp949', skiprows=4, header=0)
        # 각 csv 파일 중 원하는 행 추출
        df = df.iloc[:, [0, 1, 2]]
        # 파일 이름을 가져와서 열 이름 변경
        spl0_col_name = os.path.basename(filename) + "_SPL0"
        imp_col_name = os.path.basename(filename) + "_Imp"
        df.columns = ["Frequency", spl0_col_name, imp_col_name]

        # 파일 이름에서 확장자를 제거한 부분으로 테이블 이름 생성
        table_name = os.path.splitext(os.path.basename(filename))[0]
        # # 파일 이름을 그대로 테이블 이름으로 사용
        # table_name = os.path.basename(filename)
        # 테이블 이름에 있는 특수 문자를 '_' (밑줄)로 치환
        sanitized_table_name = re.sub(r"[^\w]", "_", table_name)

        # 텍스트 위젯에서 내용을 가져와 "text" 열에 추가
        text_content = text_widget.get("1.0", "end-1c")
        df.loc[0, "text"] = text_content  # Set the "text" column value only for the first row
        # 'text' 열의 데이터 타입을 'real'로 변경
        # df['text'] = df['text'].astype('float')

        # df["text"] = text_content  # Set the "text" column value only for the first row

        df.to_csv(os.path.join(data_folder, os.path.basename(filename)), index=False, encoding='cp949')

        # 기존 테이블에 데이터를 추가합니다.
        df.to_sql(sanitized_table_name, connection, if_exists='append', index=False)

        if sanitized_table_name in deleted_tables:
            deleted_tables.remove(sanitized_table_name)

        # 리스트박스를 비워줍니다.
        list_file.delete(0, END)

        # 데이터베이스에 저장된 테이블 이름을 리스트박스에 추가합니다.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = cursor.fetchall()
        table_names = [name[0] for name in table_names]
        table_names = [name for name in table_names if name not in deleted_tables]

        for table_name in table_names:
            list_file.insert(END, table_name)

    connection.close()

# Matplotlib 폰트 설정 (예시로 나눔고딕 폰트를 사용합니다.)
plt.rcParams["font.family"] = "NanumGothic"

# 데이터베이스 파일 이름
db_file = "data.db"

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
            # time.sleep(0.3)
            list_file.delete(selected_table_index)  # 리스트박스에서도 삭제
            # time.sleep(0.3)
            # 삭제한 테이블 이름을 리스트와 데이터베이스에서 모두 제거
            deleted_tables.append(selected_table)
            with open(deleted_tables_file, 'w') as file:
                file.write("\n".join(deleted_tables))
        except sqlite3.Error as e:
            print("Error while deleting table:", e)
        finally:
            connection.close()



# 테이블 선택 시 내용 출력
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

# 그래프를 출력할 프레임
graph_frame = tk.Frame(root)
graph_frame.pack(side=tk.RIGHT)

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

# # 그래프를 출력할 프레임
# graph_frame = tk.Frame(button_frame1)
# graph_frame.pack(side=tk.TOP)

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
selected_list.pack(side=tk.TOP,anchor="w", pady=15)

def update_or_insert_text(connection, selected_table, new_text):
    cursor = connection.cursor()
    sanitized_table = sanitize_column_name(selected_table)

    try:
        # "text" 열을 수정하고 데이터베이스에 반영합니다.
        cursor.execute(f"UPDATE {sanitized_table} SET text = ? WHERE 1", (new_text,))
        connection.commit()

        connection.commit()
    except sqlite3.Error as e:
        print("데이터베이스 업데이트 중 오류 발생:", e)

# update_text 함수 수정
def update_text():
    global selected_table

    if selected_table:
        # 수정된 텍스트 내용을 가져옵니다.
        new_text = text_widget.get("1.0", "end-1c")

        # SQLite 데이터베이스에 연결합니다.
        connection = sqlite3.connect(db_file)

        try:
            update_or_insert_text(connection, selected_table, new_text)

            # 텍스트 위젯 업데이트
            text_widget.config(state='normal')  # 텍스트 위젯 활성화
            text_widget.delete("1.0", "end")  # 현재 텍스트 삭제
            text_widget.insert("1.0", new_text)  # 새로운 텍스트 삽입
            text_widget.config(state='disabled', bg='light gray')  # 텍스트 위젯 비활성화

        finally:
            connection.close()

    else:
        print("선택한 테이블이 없습니다.")

# 텍스트 입력 위젯을 생성합니다.
text_widget = tk.Text(root, width=55, height=20)
text_widget.config(state=tk.DISABLED, bg='#CCCCCC')
text_widget.pack(side=tk.TOP, anchor='w')

# 버튼을 담을 프레임 생성
text_frame = tk.Frame(root)
text_frame.pack(side=tk.TOP, anchor='w')

# 수정 버튼 생성
edit_button = tk.Button(text_frame, text="Text modify", command=lambda: text_widget.config(state=tk.NORMAL, bg='white'))
edit_button.pack(side=tk.LEFT)

# 저장 버튼 생성
save_button = tk.Button(text_frame, text="Text save", command=update_text)
save_button.pack(side=tk.LEFT)

def on_table_select(event):
    global initial_values

    selected_table = list_file.get(list_file.curselection())

    cursor.execute(f"PRAGMA table_info({selected_table})")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    initial_values["x_col"] = column_names[0]  # x 컬럼 초기값 설정
    x_col_var.set(initial_values["x_col"])
    x_col_label.config(text="X Column: " + x_col_var.get())

    y_col_listbox.delete(0, tk.END)
    for col_name in column_names[1:]:
        y_col_listbox.insert(tk.END, col_name)
        initial_values["y_cols"].append(col_name)  # y 컬럼 초기값 설정
list_file.bind("<<ListboxSelect>>", on_table_select)


# 그래프 창을 닫는 함수
def close_graph_window():
    global graph_frame, graph_canvas
    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().destroy()
        delattr(graph_frame, 'canvas')
    if hasattr(graph_frame, 'close_button'):
        graph_frame.close_button.destroy()
        delattr(graph_frame, 'close_button')

# 그래프 초기 상태의 x, y 축 범위 저장
original_x_limits = None
original_y_limits = None

def reset_axes():
    global ax, original_x_limits, original_y_limits
    ax.set_xlim(original_x_limits)
    ax.set_ylim(original_y_limits)
    overlap_graphs()  # 오버랩 그래프 다시 그리기
    graph_frame.canvas.draw_idle()

def reset_graph():
    global ax, original_x_limits, original_y_limits
    if hasattr(ax, 'get_lines'):  # ax에 'get_lines' 속성이 있는지 확인
        reset_axes()
        plot_graph_on_move(event=None, df=ax.df, fig=None)  # global_df 대신 ax.df 사용
        text_handles.clear()

        graph_frame.canvas.draw_idle()

def show_table_contents(event):
    global ax, original_x_limits, original_y_limits, selected_table

    # 선택한 테이블을 가져옵니다.
    selected_table = list_file.get(list_file.curselection())

    if selected_table:
        show_input_frame()
        # SQLite 데이터베이스에 연결합니다.
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        sanitized_table = sanitize_column_name(selected_table)

        try:
            # 선택한 테이블에서 데이터를 가져옵니다.
            cursor.execute(f"SELECT * FROM {sanitized_table}")
            df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
            df = df.drop("text", axis=1)  # "text" 열이 있다면 삭제합니다.

            # DataFrame ( "text" 열을 제외한)를 사용하여 그래프를 그립니다.
            ax = plot_graph(df, selected_table)  # ax를 전역 변수로 저장
            ax.df = df  # 그래프와 DataFrame을 연결합니다.
            #
            # 선택한 테이블에서 "text" 열의 내용을 가져옵니다.
            cursor.execute(f"SELECT text FROM {sanitized_table}")
            text_content = cursor.fetchone()[0]

            # time.sleep(0.5)
            # 텍스트 위젯을 가져온 "text" 내용으로 업데이트합니다.
            text_widget.config(state='normal')  # 텍스트 위젯 활성화
            text_widget.delete("1.0", "end")  # 기존 내용 삭제
            text_widget.insert("1.0", text_content)  # 새로운 내용 삽입
            text_widget.config(state='disabled')  # 텍스트 위젯 비활성화

            # 그래프를 재설정할 때 원래의 x 및 y 축 범위를 저장합니다.
            original_x_limits = ax.get_xlim()
            original_y_limits = ax.get_ylim()

            # update_text 함수를 호출하여 텍스트 위젯을 업데이트합니다.
            # update_text()

        except sqlite3.Error as e:
            print("테이블에서 데이터 가져오기 중 오류 발생:", e)
        finally:
            connection.close()

    # print("Current x-axis limits:", ax.get_xlim())
    # print("Current y-axis limits:", ax.get_ylim())


# 그래프를 그리는 함수
def plot_graph(df, title, *args):
    global ax_hline, ax_vline, text_handles, legend_names, graph_type, graph_frame  # 전역 변수로 선언


    # 그래프 타입을 전역 변수로 가져옴
    graph_type = 'Line'

    fig, ax = plt.subplots(figsize=(15, 10))  # fig 객체도 생성해야 함


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
                ax.plot(df['Frequency'], df[col], *args, label=col, color=color)  # x_col 사용
                legend_names.append(col)
                i = (i + 1) % len(colors)

    plt.xlabel("Frequency")
    plt.ylabel("Value")
    plt.title(title, loc='right')
    plt.grid(True)
    plt.legend()
    plt.xscale('log')  # x축을 로그 스케일로 설정

    # x축에 주선과 보조선 추가
    x_min, x_max = ax.get_xlim()
    x_ticks_major = [tick for tick in ax.get_xticks() if x_min <= tick <= x_max]
    x_ticks_minor = [tick for tick in ax.get_xticks(minor=True) if x_min <= tick <= x_max]
    ax.set_xticks(x_ticks_major)
    ax.set_xticks(x_ticks_minor, minor=True)
    ax.xaxis.grid(True, linestyle='-', linewidth=0.8)
    ax.xaxis.grid(True, which='minor', linestyle='--', linewidth=0.5)

    # y축에 보조선 추가
    y_min, y_max = ax.get_ylim()
    y_ticks_major = range(int(y_min), int(y_max) + 1, 10)
    y_ticks_minor = range(int(y_min) + 2, int(y_max) + 1, 2)
    ax.set_yticks(y_ticks_major)
    ax.set_yticks(y_ticks_minor, minor=True)
    ax.yaxis.grid(True, linestyle='-', linewidth=0.8)
    ax.yaxis.grid(True, which='minor', linestyle='--', linewidth=0.5)

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

    # 그래프 오른쪽으로 15% 이동하기 (여백조절하기)
    fig.subplots_adjust(top=0.7, left=0.1, right=0.95)
    fig.canvas.mpl_connect('motion_notify_event', lambda event: plot_graph_on_move(event, df, fig))
    text_handles = []  # 전역 변수로 선언
    return ax  # 생성된 ax 반환

def plot_graph_on_move(event, df, fig):
    global ax_hline, ax_vline, text_handles, legend_names
    if event.inaxes:
        x, y = event.xdata, event.ydata
        ax_hline.set_ydata(y)
        ax_vline.set_xdata(x)
        for handle in text_handles:
            handle.remove()
        text_handles = []

        text_list = []  # 텍스트를 저장할 리스트
        common_prefix = None  # 공통 접두사를 저장할 변수

        if graph_type == 'Line':
            for col in df.columns[1:]:
                if "_SPL0" in col or "_Imp" in col:
                    idx = np.abs(df['Frequency'] - x).argmin()
                    x_pos, y_pos = df['Frequency'][idx], df[col][idx]
                    y_pos_text = '{:.6g}'.format(y_pos)
                    prefix = col.split('_')[0]  # 현재 항목의 접두사 추출

                    # 공통 접두사를 초기화하거나 변경합니다.
                    if common_prefix is None:
                        common_prefix = prefix
                        spl0_y = y_pos_text if "_SPL0" in col else ""
                        imp_y = y_pos_text if "_Imp" in col else ""
                    elif common_prefix != prefix:
                        # 같은 이름의 항목을 합쳐서 리스트에 추가합니다.
                        combined_text = f"{common_prefix}_SPL0({spl0_y})_IMP({imp_y})"
                        text_list.append(combined_text)
                        common_prefix = prefix
                        spl0_y = y_pos_text if "_SPL0" in col else ""
                        imp_y = y_pos_text if "_Imp" in col else imp_y
                    else:
                        spl0_y = y_pos_text if "_SPL0" in col else spl0_y
                        imp_y = y_pos_text if "_Imp" in col else imp_y

            # 십자선 좌표 추가
            coords_text = f'Hz: {x:.1f}    dB: {y:.1f}\n'
            text_list.append(coords_text)
            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(handles=handles, labels=labels, loc='lower right')

            # 마지막 항목을 리스트에 추가합니다.
            if common_prefix is not None:
                full_name = common_prefix.replace('_Imp', '').replace('.csv', '')  # _Imp와 .csv 제거
                combined_text = f"SPL({spl0_y})_IMP({imp_y})    {full_name}"
                text_list.append(combined_text)

        # 리스트의 항목을 하나의 문자열로 합칩니다.
        combined_text = "\n".join(text_list)

        # 합쳐진 텍스트를 하나의 텍스트 핸들로 표시합니다.
        if combined_text:
            handle = plt.text(0.01, 0.95, combined_text, fontsize=10,
                              transform=fig.transFigure, ha='left', va='top')
            text_handles.append(handle)

        fig.canvas.draw_idle()


fig = plt.figure()
fig.canvas.mpl_connect('motion_notify_event', lambda event: plot_graph_on_move(event, global_df, fig))

def overlap_graphs():
    global global_df, text_handles, ax_hline, ax_vline, colors  # 전역 변수로 선언
    global_df = None  # global_df 변수 초기화

    selected_columns = selected_list.get(0, tk.END)
    if len(selected_columns) == 0:
        return

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()  # cursor 정의

    plt.clf()  # 기존 그래프 초기화

    legend_names = []  # 범례 이름들을 저장할 리스트
    colors = ['k', 'r', 'b', 'g', 'm', 'y', 'k']  # 색상 리스트 생성
    i = 0  # 색상 인덱스
    axs = []  # 각 그래프의 ax 객체를 보관하는 리스트

    df_list = []  # 각 데이터프레임을 저장할 리스트

    for col in selected_columns:
        cursor.execute(f"SELECT * FROM {col}")
        df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
        df = df.drop("text", axis=1)  # "text" 열이 있다면 삭제합니다.
        if 'Frequency' not in df.columns:
            connection.close()
            return

        color = colors[i]
        ax = plt.semilogx(df['Frequency'], df.iloc[:, 1:], label=col, color=color)
        axs.append(ax)

        legend_names.append(col)
        i = (i + 1) % len(colors)

        df_list.append(df)  # 데이터프레임을 리스트에 추가

    # 모든 데이터프레임을 병합하여 하나의 데이터프레임으로 만듦
    global_df = pd.concat(df_list, axis=1)
    global_df = global_df.loc[:, ~global_df.T.duplicated()]  # 동일한 X축 하나로 병합

    # print("\033[93m" + "Global DataFrame Created:" + "\033[0m")
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(global_df)

    plt.xlabel("Frequency")
    plt.ylabel("Value")
    plt.title("Overlapping Graphs")
    plt.grid(True)
    plt.legend()
    plt.xscale('log')

    # 그래프를 tkinter 창에 출력
    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().pack_forget()  # 기존 그래프 제거

    graph_frame.canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_frame)
    graph_frame.canvas.draw()
    graph_frame.canvas.get_tk_widget().pack()

    ax = plt.gca()  # 현재 Axes 객체를 가져옴

    # x축에 주선과 보조선 추가
    x_min, x_max = ax.get_xlim()
    x_ticks_major = [tick for tick in ax.get_xticks() if x_min <= tick <= x_max]
    x_ticks_minor = [tick for tick in ax.get_xticks(minor=True) if x_min <= tick <= x_max]
    ax.set_xticks(x_ticks_major)
    ax.set_xticks(x_ticks_minor, minor=True)
    ax.xaxis.grid(True, linestyle='-', linewidth=0.8)
    ax.xaxis.grid(True, which='minor', linestyle='--', linewidth=0.5)

    # y축에 주선과 보조선 추가
    y_min, y_max = ax.get_ylim()
    y_ticks_major = range(int(y_min), int(y_max) + 1, 10)
    y_ticks_minor = range(int(y_min) + 2, int(y_max) + 1, 2)
    ax.set_yticks(y_ticks_major)
    ax.set_yticks(y_ticks_minor, minor=True)
    ax.yaxis.grid(True, linestyle='-', linewidth=0.8)
    ax.yaxis.grid(True, which='minor', linestyle='--', linewidth=0.5)

    handles, labels = ax.get_legend_handles_labels()  # 현재 Axes의 legend 정보를 가져옴
    ax.legend(handles=handles, labels=labels, loc='best')  # 범례 위치를 조정

    ax_hline = ax.axhline(y=0, color='k', linewidth=1, linestyle='--')
    ax_vline = ax.axvline(x=0, color='k', linewidth=1, linestyle='--')

    fig = plt.gcf()  # 현재 그래프의 fig 객체를 가져옴
    fig.canvas.mpl_connect('motion_notify_event', lambda event: overlap_graphs_on_move(event, global_df, fig))

    connection.close()

    text_handles = []  # 전역 변수로 선언

# overlap_graphs 함수 내에서의 on_move 함수 정의
def overlap_graphs_on_move(event, global_df, fig):
    global text_handles, legend_names, colors
    if event.inaxes:
        x, y = event.xdata, event.ydata
        for handle in text_handles:
            handle.remove()
        text_handles = []

        if graph_type == 'Line':
            ax = plt.gca()
            idx = np.abs(global_df['Frequency'] - x).idxmin()
            x_pos = global_df['Frequency'][idx]
            text_dict = {}  # 파일 이름을 키로 가지는 딕셔너리

            for col in global_df.columns[1:]:
                if "_SPL0" in col or "_Imp" in col:
                    y_pos = global_df[col][idx]
                    spl0_y = '{:.6g}'.format(y_pos) if "_SPL0" in col else ""
                    imp_y = '{:.6g}'.format(y_pos) if "_Imp" in col else ""
                    file_name = os.path.splitext(col)[0]  # 파일 이름 추출 (확장자 제외)

                    if file_name not in text_dict:
                        text_dict[file_name] = {'SPL0': spl0_y, 'IMP': imp_y}
                    else:
                        if "_SPL0" in col:
                            text_dict[file_name]['SPL0'] = spl0_y
                        elif "_Imp" in col:
                            text_dict[file_name]['IMP'] = imp_y

            y_offsets = [0]
            y_offset_step = 5  # 텍스트 핸들 간의 간격
            for file_name, values in text_dict.items():
                combined_text = f"{file_name}_SPL0({values['SPL0']})_IMP({values['IMP']})"
                x_display, y_display = ax.transData.transform((x_pos, y))
                x_display = max(x_display, ax.transData.transform((0, 0))[0] + 10)
                y_display = min(y_display, ax.transData.transform((0, ax.get_ylim()[0]))[1] + 30)



                first_handle_offset = 0
                y_offset = first_handle_offset
                for offset in y_offsets:
                    if abs(y_display - offset) < 20:
                        y_display += y_offset_step  # 겹치는 경우 간격을 늘립니다.

                y_offsets.append(y_display)


                # 텍스트 핸들의 y 위치를 그래프의 y 범위 내로 조정
                y_display = max(y_display, ax.transData.transform((0, ax.get_ylim()[0]))[1] + 5)
                y_display = min(y_display, ax.transData.transform((0, ax.get_ylim()[1]))[1] - 5)

                # 텍스트 핸들의 y 위치를 그래프의 y 범위 밖으로 나가지 않도록 수정
                y_display = max(y_display, ax.transData.transform((0, 0))[1])
                y_display = min(y_display, ax.transData.transform((0, ax.get_ylim()[1]))[1])

                text_handle = ax.text(8, y_display, combined_text, fontsize=10, ha='left', va='bottom', rotation=0)
                text_handles.append(text_handle)
                # Legend 추가 전에 handles와 labels 가져오기
                handles, labels = ax.get_legend_handles_labels()

                legend = ax.legend(handles=handles, labels=labels, loc='lower right')  # 범례를 오른쪽 아래에 배치합니다.
            # 십자선 좌표 추가
            coords_text = f'Hz: {x:.1f}    dB: {y:.1f}\n'
            text_handle = plt.text(0.48, 0.05, coords_text, fontsize=10, ha='left', va='top',
                                   transform=fig.transFigure)
            text_handle.set_color('black')  # 검정색으로 설정
            text_handles.append(text_handle)

            text_colors = [colors[i % len(colors)] for i in range(len(text_handles))]
            text_colors[-1] = 'black'  # 마지막 항목(십자선 텍스트)의 색상을 검정으로 설정

            for text_handle, color in zip(text_handles, text_colors):
                text_handle.set_color(color)

            fig.canvas.draw_idle()


fig = plt.figure()
fig.canvas.mpl_connect('motion_notify_event', lambda event: overlap_graphs_on_move(event, global_df, fig))

# 겹치기 버튼 생성
overlap_button = tk.Button(button_frame, text="Overlap Graphs", command=overlap_graphs)
overlap_button.pack(side=tk.LEFT)

def reset_overlapping_graphs():
    global text_handles, legend_names
    # 그래프 및 관련 객체 초기화
    plt.clf()  # 그래프 초기화
    if hasattr(graph_frame, 'canvas'):
        graph_frame.canvas.get_tk_widget().destroy()
        delattr(graph_frame, 'canvas')
    if hasattr(graph_frame, 'close_button'):
        graph_frame.close_button.destroy()
        delattr(graph_frame, 'close_button')
    text_handles = []
    legend_names = []

    # listbox2 내용 초기화
    selected_list.delete(0, tk.END)  # 리스트 박스 내용 삭제

# 오버랩 그래프 리셋 버튼 생성
reset_overlap_button = tk.Button(button_frame, text="Reset", command=reset_overlapping_graphs)
reset_overlap_button.pack(side=tk.LEFT)

# 리스트박스가 변경되었을 때 show_table_contents 함수를 호출하도록 바인딩
list_file.bind('<<ListboxSelect>>', show_table_contents)



def adjust_axis_scale():
    global initial_values  # Access the global initial_values dictionary
    x_min_text = x_min_entry.get()
    x_max_text = x_max_entry.get()
    y_min_text = y_min_entry.get()
    y_max_text = y_max_entry.get()
    ax = plt.gca()

    if x_min_text or x_max_text:
        x_min = float(x_min_text) if x_min_text else None
        x_max = float(x_max_text) if x_max_text else None

        if x_min == 0:
            messagebox.showwarning("Warning", "X축 최소값으로 0보다 큰 값을 입력해주세요.")
            return

        ax.set_xlim(x_min, x_max)

        if x_min == 0.01:
            ax.set_xticks([0, x_max])

    if y_min_text or y_max_text:
        y_min = float(y_min_text) if y_min_text else None
        y_max = float(y_max_text) if y_max_text else None

        if y_min == 0:
            messagebox.showwarning("Warning", "Y축 최소값으로 0보다 큰 값을 입력해주세요.")
            return

        ax.set_ylim(y_min, y_max)

        if y_min == 0.01:
            ax.set_yticks([0, y_max])

    graph_frame.canvas.draw()



# 그래프 영역 아래에 입력 요소 및 스케일 조정 버튼 배치
input_frame = tk.Frame(graph_frame)
input_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

# 입력 요소를 숨김 (처음에는 숨겨진 상태)
input_frame.grid_remove()

# x축 및 y축 라벨
x_label = tk.Label(input_frame, text="X-axis:", anchor="w")
x_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
y_label = tk.Label(input_frame, text="Y-axis:", anchor="w")
y_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

# x축 최소값 입력
x_min_label = tk.Label(input_frame, text="Min:")
x_min_label.grid(row=0, column=4, padx=5, pady=5)
x_min_entry = tk.Entry(input_frame)
x_min_entry.grid(row=0, column=5, padx=5, pady=5)

# x축 최대값 입력
x_max_label = tk.Label(input_frame, text="Max:")
x_max_label.grid(row=0, column=6, padx=5, pady=5)
x_max_entry = tk.Entry(input_frame)
x_max_entry.grid(row=0, column=7, padx=5, pady=5)

# y축 최소값 입력
y_min_label = tk.Label(input_frame, text="Min:")
y_min_label.grid(row=1, column=4, padx=5, pady=5)
y_min_entry = tk.Entry(input_frame)
y_min_entry.grid(row=1, column=5, padx=5, pady=5)

# y축 최대값 입력
y_max_label = tk.Label(input_frame, text="Max:")
y_max_label.grid(row=1, column=6, padx=5, pady=5)
y_max_entry = tk.Entry(input_frame)
y_max_entry.grid(row=1, column=7, padx=5, pady=5)

# 스케일 조정 버튼
scale_button = tk.Button(input_frame, text="Adjust Axis", command=adjust_axis_scale)
scale_button.grid(row=0, column=8, rowspan=2, padx=5, pady=5)

# 리셋 버튼
reset_button = tk.Button(input_frame, text="Reset Graph", command=reset_graph)
reset_button.grid(row=0, column=9, rowspan=2, padx=5, pady=5)

# 입력 요소를 숨기는 함수
def hide_input_frame():
    input_frame.pack_forget()

# 입력 요소를 나타내는 함수
def show_input_frame():
    input_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

# 처음에는 입력 요소를 숨김
hide_input_frame()

root.mainloop()