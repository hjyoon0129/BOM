import pandas as pd
import sqlite3
import os
from tkinter import Tk, Button, Listbox, END, filedialog, messagebox
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.font_manager import FontProperties
import numpy as np


# 폰트 경로를 설정합니다.
font_path = r"C:\Users\SAMSUNG\AppData\Local\Microsoft\Windows\Fonts\현대하모니 M.ttf"

# Matplotlib의 폰트 매니저에 폰트 경로를 추가합니다.
plt.rcParams['font.family'] = FontProperties(fname=font_path).get_name()

def close_event():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        plt.close('all')
        root.destroy()  # Tkinter 창 종료
        # 메타플롯립의 모든 그래프 내용 삭제

# tkinter 창 생성
root = Tk()
root.title("CSV Table Viewer")
root.geometry("1500x700")
root.protocol("WM_DELETE_WINDOW", close_event)  # 창이 닫힐 때 close_event 호출

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


def on_table_select(event):
    selected_table = list_file.get(list_file.curselection())

    cursor.execute(f"PRAGMA table_info({selected_table})")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    x_col_var.set(column_names[0])
    x_col_label.config(text="X Column: " + x_col_var.get())

    y_col_listbox.delete(0, tk.END)
    for col_name in column_names[1:]:
        y_col_listbox.insert(tk.END, col_name)
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

# 그래프를 그리는 함수
def plot_graph(df, title, *args):
    global ax_hline, ax_vline, text_handles, legend_names, graph_type  # 전역 변수로 선언

    # 그래프 타입을 전역 변수로 가져옴
    graph_type = 'Line'

    fig, ax = plt.subplots(figsize=(11, 10))  # fig 객체도 생성해야 함

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
    fig.subplots_adjust(left=0.5, right=0.95)
    fig.canvas.mpl_connect('motion_notify_event', lambda event: plot_graph_on_move(event, df, fig))
    text_handles = []  # 전역 변수로 선언

def plot_graph_on_move(event, df, fig):
    global ax_hline, ax_vline, text_handles, legend_names
    if event.inaxes:
        x, y = event.xdata, event.ydata
        ax_hline.set_ydata(y)
        ax_vline.set_xdata(x)
        for handle in text_handles:
            handle.remove()
        text_handles = []
        if graph_type == 'Line':
            for col in df.columns[1:]:
                if "_SPL0" in col or "_Imp" in col:
                    idx = np.abs(df['Frequency'] - x).argmin()
                    x_pos, y_pos = df['Frequency'][idx], df[col][idx]
                    x_pos_text = '{:.6g}'.format(x_pos)
                    y_pos_text = '{:.6g}'.format(y_pos)
                    text = f'{col}: ({x_pos_text}, {y_pos_text})'
                    if "_SPL0" in col:  # Only add text for _SPL0 and _Imp columns
                        handle = plt.text(0.01, 0.95 - (0.05 * (legend_names.index(col))), text, fontsize=10,
                                          transform=fig.transFigure, ha='left')
                        text_handles.append(handle)
                    if "_Imp" in col:
                        handle = plt.text(0.01, 0.95 - (0.05 * (legend_names.index(col))), text, fontsize=10,
                                          transform=fig.transFigure, ha='left')
                        text_handles.append(handle)
        fig.canvas.draw_idle()

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

    handles, labels = plt.gca().get_legend_handles_labels()  # 현재 Axes의 legend 정보를 가져옴
    plt.gca().legend(handles=handles, labels=labels, loc='best')  # 범례 위치를 조정

    ax_hline = plt.gca().axhline(y=0, color='k', linewidth=1, linestyle='--')
    ax_vline = plt.gca().axvline(x=0, color='k', linewidth=1, linestyle='--')

    fig = plt.gcf()  # 현재 그래프의 fig 객체를 가져옴
    fig.canvas.mpl_connect('motion_notify_event', lambda event: overlap_graphs_on_move(event, global_df, fig))

    connection.close()

    text_handles = []  # 전역 변수로 선언

# overlap_graphs 함수 내에서의 on_move 함수 정의
def overlap_graphs_on_move(event, global_df, fig):
    global text_handles, legend_names, colors
    if event.inaxes:
        x, y = event.xdata, event.ydata
        ax_hline.set_ydata([y] * len(ax_hline.get_xdata()))
        ax_vline.set_xdata([x] * len(ax_vline.get_ydata()))
        for handle in text_handles:
            handle.remove()
        text_handles = []
        if graph_type == 'Line':
            ax = plt.gca()
            idx = np.abs(global_df['Frequency'] - x).argmin()
            x_pos = global_df['Frequency'][idx]
            x_pos_text = '{:.6g}'.format(x_pos)
            y_positions = []

            for col in global_df.columns[1:]:
                if "_SPL0" in col or "_Imp" in col:
                    y_pos = global_df[col][idx]
                    y_pos_text = '{:.6g}'.format(y_pos)
                    text = f'{col}: ({x_pos_text}, {y_pos_text})'

                    x_display, y_display = ax.transData.transform((x_pos, y_pos))
                    # 텍스트가 그래프 영역을 벗어나지 않도록 좌표 제어
                    x_display = max(x_display, ax.transData.transform((0, 0))[0] + 10)  # x 좌표
                    y_display = min(y_display, ax.transData.transform((0, ax.get_ylim()[0]))[1] - 10)  # y 좌표


                    while y_display in y_positions:
                        y_display += -5

                    y_positions.append(y_display)

                    # bbox 스타일 설정하여 배경색을 흰색으로 설정
                    text_handle = ax.text(0.005, y_display, text, fontsize=10, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=1.0)) #alpha : text box 투명도, face color: textbox 배경색
                    text_handles.append(text_handle)

            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(handles=handles, labels=labels, loc='lower right')

        text_colors = []
        color_idx = 0

        for col in global_df.columns[1:]:
            if "_SPL0" in col or "_Imp" in col:
                text_colors.append(colors[color_idx])
                if "_Imp" in col:
                    color_idx = (color_idx + 1) % len(colors)

        for text_handle, color in zip(text_handles, text_colors):
            text_handle.set_color(color)  # 텍스트 핸들의 색상 설정

        fig.canvas.draw_idle()

fig = plt.figure()

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

root.mainloop()