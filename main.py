import sqlite3


conn = sqlite3.connect("mydb.sqlite")

cursor = conn.cursor()

cursor.executescript("""create table if not exists authors(id integer primary key autoincrement, 
                                                    name text(30));
                  create table if not exists status(id integer primary key, 
                                                    status_name text(20));
                  create table if not exists book(id integer primary key not null, 
                                                 title text, author integer, year integer, status real,
                                                 foreign key (author) references authors (id),
                                                 foreign key (status) references status (id));
                   """)
# print(bool(cursor.execute("select id from status").fetchall()) is False)
if bool(cursor.execute("select id from status").fetchall()) is False:
    cursor.execute(
        f'insert into status (status_name) values ("в наличии"), ("выдана");')
    conn.commit()


class Book:
    """
    Класс книги, которая собственно хранит информацию о книге
    """

    def __init__(self, title: str, author: str, year: str, status: int):
        self.title = title
        self.author = author
        self.year = year
        self.status = status

    def __str__(self) -> str:
        return "title, author, year, status"


class Author:
    """
    Класс автора, которая собственно хранит информацию о книге
    """

    def __init__(self, name):
        self.name = name


class Status:
    """
    Класс статуса, которая собственно хранит информацию о книге
    """

    def __init__(self, status_name):
        self.status_name = status_name


class Connection:
    """
        Собственно класс, через который мы производим все вариации с нашей информацией. Добавление книги, автора, статуса,
        поиск книги, удаление книги, вывод списка книг
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def add_book(self, book: Book):
        "Функция для добавление книги в БД. Принимает в себя объект класса Book"
        author_id = self.cursor.execute(f"""select id from authors where name =
                                        '{book.author}'""").fetchone()[0]
        if not author_id:
            author_id = self.add_author(Author(book.author))
        self.cursor.execute(f"""insert into book({str(book)}) values
                            ('{book.title}', {author_id}, {book.year}, {book.status})""")
        self.conn.commit()

    def add_status(self, status: Status):
        "Функция для добавление статуса в БД. Принимает в себя объект класса Status"
        status_names = self.cursor.execute(
            "select status_name from status").fetchall()
        if status not in status_names:
            self.cursor.execute(
                f"insert into status(status_name) values ({status.status_name})")
            self.conn.commit()
        return self.cursor.execute(f"select id from status where status_name = '{status.status_name}'").fetchone()[0]

    def add_author(self, author: Author):
        "Функция для добавление автора в БД. Принимает в себя объект класса Author"
        authors_names = self.cursor.execute(
            "select name from authors").fetchall()
        if author not in authors_names:
            self.cursor.execute(
                f"insert into authors(name) values ('{author.name}')")
            self.conn.commit()
        return self.cursor.execute(f"select id from authors where name = '{author.name}'").fetchone()[0]

    def remove_book(self, id_book):
        """Удаление книги из БД. При попытке удаления несуществующей книги, получаем сообщение по этому поводу"""
        try:
            self.cursor.execute(f"delete from book where id = {id_book}")
            self.conn.commit()
        except:
            print("Нет книги с таким идентификатором")

    def search_book_for_title(self, title):
        """Поиск книги по названию"""
        books = self.cursor.execute(
            f"select * from book where title = '{title}'").fetchall()
        if books:
            return books
        else:
            return ["Не найдены книги по данному имени"]

    def search_book_for_author(self, author_name):
        """Поиск книги по автору"""
        books = self.cursor.execute(
            f"select * from book where book.author in (select id from authors where name = '{author_name}')").fetchall()
        if books:
            return books
        else:
            return ["Не найдены книги по данному автору"]

    def search_book_for_year(self, year):
        """Поиск книги по году издания"""
        books = self.cursor.execute(
            f"select * from book where year = {year}").fetchall()
        if books:
            return books
        else:
            return ["Не найдены книги изданные в этот год"]

    def print_books(self):
        books = self.cursor.execute(f"select * from book").fetchall()
        for book in books:
            print(*book, sep="\t")
            break
        else:
            print("В библиотеке нет книг")

    def set_status(self, id_book, status_id):
        try:
            self.cursor.execute(f"""update book
                                set status = {status_id}
                                where id = {id_book}""")
            self.conn.commit()
        except:
            print('Введены некорректные данные')


my_connection = Connection(conn=conn)

while True:
    query = int(input("""Что вы хотите сделать сейчас?
1. Добавить книгу;
2. Удалить книгу;
3. Найти книгу;
4. Получить список всех книг;
5. Изменить статус книги.\n"""))
    if query == 1:
        title = input("Введите название книги: ")
        author_name = input("Введите имя автора: ")
        year = int(input("Введите год издания книги: "))
        status = input("Введите статус книги: (в наличии-1, выдана-2): ")
        my_connection.add_book(Book(title, author_name, year, status))
    elif query == 2:
        id = input("Введите id книги, которую хотите удалить: ")
        my_connection.remove_book(id)
    elif query == 3:
        print("""Для поиска книги: 
по названию, введите 1;
по автору, введите 2;
по году издания, введите 3""")
        query = int(input())
        if query == 1:
            print(*my_connection.search_book_for_title(
                input("Введите название книги: ")), sep="\n")
        elif query == 2:
            print(*my_connection.search_book_for_author(input("Введите имя автора: ")), sep="\n")
        elif query == 3:
            print(*my_connection.search_book_for_year(
                int(input("Введите год издания: "))), sep="\n")
        else:
            print("Введено некорректное значение")
    elif query == 4:
        my_connection.print_books()
    elif query == 5:
        my_connection.set_status(int(input("Введите идентификатор книги, которую хотите изменить: ")),
                                 input("Введите новый статус книги ('в наличии'-1, 'выдана'-2): "))
    else:
        print("Введено некорректное значение")
