import mysql.connector
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk
import io

# MySQL 연결 설정
mydb = mysql.connector.connect(
    host="192.9.0.95",
    user="Yoon",
    password="dream",
    database="y"
)

# GUI 생성
root = Tk()
root.title("도서 검색")

# 검색 함수
def search_books():
    # 검색어 가져오기
    search_text = search_entry.get()
    # 데이터베이스에서 검색하기
    cursor = mydb.cursor()
    sql = "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s"
    val = ("%" + search_text + "%", "%" + search_text + "%")
    cursor.execute(sql, val)
    results = cursor.fetchall()
    # 결과 출력하기
    result_listbox.delete(0, END)
    for result in results:
        result_listbox.insert(END, result[1])


# 입력 함수
def add_book_window():
    # 새 창 생성
    add_book_window = Toplevel(root)
    add_book_window.title("도서 추가")

    # 입력 폼 생성
    title_frame = Frame(add_book_window)
    title_frame.pack()
    title_label = Label(title_frame, text="제목:")
    title_label.pack(side=LEFT)
    title_entry = Entry(title_frame)
    title_entry.pack(side=LEFT)

    author_frame = Frame(add_book_window)
    author_frame.pack()
    author_label = Label(author_frame, text="저자:")
    author_label.pack(side=LEFT)
    author_entry = Entry(author_frame)
    author_entry.pack(side=LEFT)

    year_frame = Frame(add_book_window)
    year_frame.pack()
    year_label = Label(year_frame, text="출판년도:")
    year_label.pack(side=LEFT)
    year_entry = Entry(year_frame)
    year_entry.pack(side=LEFT)

    image_button = Button(add_book_window, text="그림 파일 선택", command=lambda: select_image(add_book_window))
    image_button.pack()

    save_button = Button(add_book_window, text="저장",
                         command=lambda: save_book(add_book_window, title_entry, author_entry, year_entry))
    save_button.pack()

    # 그림 파일 선택 함수
    def select_image(window):
        image_file = filedialog.askopenfilename()
        if image_file:
            image_preview = PhotoImage(file=image_file)
            image_label = Label(window, image=image_preview)
            image_label.image = image_preview
            image_label.pack()

# 저장 함수
def save_book(window, title_entry, author_entry, year_entry):
    # 텍스트 가져오기
    title = title_entry.get()
    author = author_entry.get()
    year = int(year_entry.get())
    # 그림 파일 가져오기
    image_label = window.winfo_children()[-2]
    image = None
    if image_label.winfo_exists():
        image = image_label.cget("image").__str__()
    # 데이터베이스에 저장하기
    cursor = mydb.cursor()
    sql = "INSERT INTO books (title, author, year, image) VALUES (%s, %s, %s, %s)"
    val = (title, author, year, image)
    cursor.execute(sql, val)
    mydb.commit()
    window.destroy()

def show_book():
    # 선택한 항목의 인덱스 가져오기
    selected_book = book_listbox.curselection()
    if len(selected_book) == 0:
        return
    selected_index = selected_book[0]

    # 선택한 항목의 id 가져오기
    selected_text = book_listbox.get(selected_index)
    selected_id = int(selected_text.split("-")[0].strip())

    # 데이터베이스 연결
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # 데이터 조회
    query = "SELECT title, author, year, image FROM books WHERE id = %s"
    cursor.execute(query, (selected_id,))
    book = cursor.fetchone()

    # 데이터를 오른쪽 프레임에 보여주기
    title_label.config(text=f"제목: {book[0]}")
    author_label.config(text=f"작가: {book[1]}")
    year_label.config(text=f"출판년도: {book[2]}")

    # 이미지를 파일로 저장한 후, 오른쪽 프레임에 표시
    image_data = book[3]
    if image_data is not None:
        with open("temp.jpg", "wb") as f:
            f.write(image_data)
        image = Image.open("temp.jpg")
        image = image.resize((200, 200))


# 입력 버튼 생성
add_button = Button(root, text="도서 추가", command=add_book_window)
add_button.pack()

# 검색 폼 생성
search_frame = Frame(root)
search_frame.pack()
search_label = Label(search_frame, text="검색어:")
search_label.pack(side=LEFT)
search_entry = Entry(search_frame)
search_entry.pack(side=LEFT)
search_button = Button(search_frame, text="검색", command=search_books)
search_button.pack(side=LEFT)

# 검색 결과 표시할 리스트박스 생성
result_listbox = Listbox(root)
result_listbox.pack()

root.mainloop()