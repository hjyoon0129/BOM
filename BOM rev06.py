import pandas as pd
import sqlite3
import os
from tkinter import Tk, Button, Listbox, END, filedialog

# tkinter 창 생성
root = Tk()
root.title("CSV Table Viewer")
root.geometry("600x600")

# 데이터폴더 경로
data_folder = "data"

# 데이터폴더가 없을 경우 생성
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# 데이터베이스 연결
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# 데이터베이스에 저장된 테이블 이름 가져오기
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()
table_names = [name[0] for name in table_names]

# 데이터베이스 연결 종료
connection.close()

csv_filenames = []  # 선택한 CSV 파일 이름 리스트

# CSV 파일을 선택하는 함수
def select_csv_files():
    global csv_filenames
    csv_filenames = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    csv_button.config(text="Selected: {} file(s)".format(len(csv_filenames)))
    # 선택한 파일 목록 표시
    list_file.delete(0, END)
    for file in csv_filenames:
        list_file.insert(END, os.path.basename(file))

# CSV 파일 선택 버튼
csv_button = Button(root, text="Select CSV File", command=select_csv_files)
csv_button.pack()

# 데이터베이스에 CSV 파일을 저장하는 함수
def save_csv_to_database():
    global csv_filenames
    connection = sqlite3.connect('data.db')
    for filename in csv_filenames:
        # 1~4번째 라인을 스킵하고 5번째 라인부터 데이터를 읽어들임
        df = pd.read_csv(filename, encoding='latin-1', skiprows=4, header=0)
        # 각 csv파일중 원하는 행 추출
        df = df.iloc[:, [0, 1, 2]]
        # 파일 이름을 가져와서 열 이름 변경
        spl0_col_name = os.path.basename(filename) + "_SPL0"
        imp_col_name = os.path.basename(filename) + "_Imp"
        df.columns = ["Frequency", spl0_col_name, imp_col_name]

        # 파일 이름을 사용하여 데이터폴더에 가공된 CSV 파일을 저장
        csv_filename = os.path.join(data_folder, os.path.basename(filename))
        df.to_csv(csv_filename, index=False)

        # 데이터프레임을 SQLite 테이블로 저장
        table_name = os.path.splitext(os.path.basename(filename))[0]
        df.to_sql(table_name, connection, if_exists='replace', index=False)

    # 리스트박스에 데이터베이스에 저장된 테이블 이름 추가
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]
    list_file.delete(0, END)
    for table_name in table_names:
        list_file.insert(END, table_name)

    connection.close()

# 리스트박스에 데이터베이스에 저장된 테이블 이름 추가
list_file = Listbox(root, width=50, height=10)
for table_name in table_names:
    list_file.insert(END, table_name)
list_file.pack()

# CSV 파일 저장 버튼
save_button = Button(root, text="Save CSV to Database", command=save_csv_to_database)
save_button.pack()

# 리스트박스에 보여지는 테이블 이름이 변경되면 선택된 테이블의 내용을 보여주는 함수
def show_table_contents(event):
    selected_table = list_file.get(list_file.curselection())
    if selected_table:
        connection = sqlite3.connect('data.db')
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", connection)
        connection.close()

        # 여기서 선택한 테이블의 내용을 출력하도록 하세요
        print(df)

# 리스트박스가 변경되었을 때 show_table_contents 함수를 호출하도록 바인딩
list_file.bind('<<ListboxSelect>>', show_table_contents)

root.mainloop()
