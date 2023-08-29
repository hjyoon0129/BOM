import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # pandas 라이브러리 임포트
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def plot_graph_on_move(event, df, fig):
    # 그래프 조정 코드
    x_min = float(x_min_entry.get())
    x_max = float(x_max_entry.get())
    y_min = float(y_min_entry.get())
    y_max = float(y_max_entry.get())
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    fig.canvas.draw_idle()


# 그래프 그리는 함수
def plot_graph(df, title, *args):
    global ax_hline, ax_vline, text_handles, legend_names, graph_type, selected_information, x_min_entry, x_max_entry, y_min_entry, y_max_entry

    # 그래프 그리기 코드
    fig, ax = plt.subplots(figsize=(15, 10))
    # ... (이전의 그래프 그리기 코드)

    # 그래프를 tkinter 창에 출력 코드
    # ... (이전의 그래프 출력 코드)

    # x축 및 y축 최소 최대값 입력란 생성
    x_min_label = tk.Label(root, text="X-axis Min:")
    x_min_label.pack()
    x_min_entry = tk.Entry(root)
    x_min_entry.pack()

    x_max_label = tk.Label(root, text="X-axis Max:")
    x_max_label.pack()
    x_max_entry = tk.Entry(root)
    x_max_entry.pack()

    y_min_label = tk.Label(root, text="Y-axis Min:")
    y_min_label.pack()
    y_min_entry = tk.Entry(root)
    y_min_entry.pack()

    y_max_label = tk.Label(root, text="Y-axis Max:")
    y_max_label.pack()
    y_max_entry = tk.Entry(root)
    y_max_entry.pack()

    # 그래프 움직임에 반응하는 이벤트 설정
    fig.canvas.mpl_connect('motion_notify_event', lambda event: plot_graph_on_move(event, df, fig))

    root.mainloop()


# 예제 데이터 프레임
np.random.seed(0)
x = np.linspace(0.1, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
df = pd.DataFrame({'x': x, 'sin(x)': y1, 'cos(x)': y2})

# Tkinter 창 생성
root = tk.Tk()
root.title("Graph Plotter")

# 버튼 클릭 시 그래프 그리기
plot_button = tk.Button(root, text="Plot Graph", command=lambda: plot_graph(df, "Graph Title"))
plot_button.pack()

root.mainloop()
