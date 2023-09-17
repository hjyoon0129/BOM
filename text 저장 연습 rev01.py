import tkinter as tk
import sqlite3


def add_to_listbox_and_database():
    # 입력 창에서 텍스트 가져오기
    text = entry.get()

    if text:
        # 리스트 박스에 항목 추가
        listbox.insert(tk.END, text)

        # SQLite 데이터베이스에 저장
        connection = sqlite3.connect("my_database.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS my_table (item TEXT)")
        cursor.execute("INSERT INTO my_table (item) VALUES (?)", (text,))
        connection.commit()
        connection.close()

        # 입력 창 비우기
        entry.delete(0, tk.END)


def save_text_widget():
    # 선택한 리스트 항목 가져오기
    selected_item = listbox.get(tk.ACTIVE)

    if selected_item:
        # 텍스트 위젯 내용 가져오기
        text_content = text_widget.get("1.0", tk.END)

        # SQLite 데이터베이스에 저장
        connection = sqlite3.connect("my_database.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS text_table (item TEXT, text_content TEXT)")

        # 이미 저장된 내용이 있는지 확인하고 업데이트 또는 삽입
        cursor.execute("SELECT * FROM text_table WHERE item=?", (selected_item,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute("UPDATE text_table SET text_content=? WHERE item=?", (text_content, selected_item))
        else:
            cursor.execute("INSERT INTO text_table (item, text_content) VALUES (?, ?)", (selected_item, text_content))

        connection.commit()
        connection.close()


def display_selected_item(event):
    # 리스트 박스에서 선택한 항목 가져오기
    selected_item = listbox.get(tk.ACTIVE)

    # 선택한 항목과 연관된 텍스트 내용 가져오기
    connection = sqlite3.connect("my_database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT text_content FROM text_table WHERE item=?", (selected_item,))
    text_content = cursor.fetchone()
    connection.close()

    # 텍스트 위젯에 표시
    text_widget.delete("1.0", tk.END)  # 기존 내용 지우기
    if text_content:
        text_widget.insert("1.0", text_content[0])


# Tkinter 윈도우 생성
window = tk.Tk()
window.title("리스트와 SQLite")

# 입력 창 생성
entry = tk.Entry(window)
entry.pack()

# 추가 버튼 생성
add_button = tk.Button(window, text="추가", command=add_to_listbox_and_database)
add_button.pack()

# 리스트 박스 생성
listbox = tk.Listbox(window)
listbox.pack()
listbox.bind("<<ListboxSelect>>", display_selected_item)  # 리스트 박스 항목 선택 이벤트

# SQLite 데이터베이스 연결
connection = sqlite3.connect("my_database.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS my_table (item TEXT)")

# 데이터베이스에서 데이터 불러와서 리스트 박스에 추가
cursor.execute("SELECT * FROM my_table")
for row in cursor.fetchall():
    listbox.insert(tk.END, row[0])

connection.close()

# 텍스트 위젯 생성
text_widget = tk.Text(window, height=5, width=40)
text_widget.pack()

# 저장 버튼 생성
save_button = tk.Button(window, text="저장", command=save_text_widget)
save_button.pack()

# 윈도우 실행
window.mainloop()
