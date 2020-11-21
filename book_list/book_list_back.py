import psycopg2

class Database:
    """ class to handle communication with Postgres database storing book and author info """

    def __init__(self, DATABASE_URL, sslmode):
        self.conn = psycopg2.connect(DATABASE_URL, sslmode=sslmode)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS author (id SMALLSERIAL PRIMARY KEY, first_name TEXT, surname TEXT, photo_url VARCHAR(255), date_birth DATE, date_death DATE)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS book_list (id SMALLSERIAL PRIMARY KEY, title TEXT, year INTEGER, isbn VARCHAR(13), author_id INTEGER)")
        self.conn.commit()

# book_list table methods
    def get_all_books(self):
        self.cur.execute("SELECT book_list.id, title, first_name, surname, year, isbn, author_id FROM book_list LEFT JOIN author ON book_list.author_id=author.id ORDER BY surname, first_name, title")
        rows = self.cur.fetchall()
        return rows;

    # creates a new book_list record => id of new record
    def add_book(self, title, author_first_name, author_surname, year, isbn):
        if isinstance(year, int) and  len(isbn) <= 13:
            author_id = self.get_author_by_name(author_first_name, author_surname)
            if author_id == 0:
                author_id = self.add_author(author_first_name, author_surname, "", "", "")
            # add book
            self.cur.execute("INSERT INTO book_list(title, year, isbn, author_id) VALUES(%s, %s, %s, %s) RETURNING id", (title, year, isbn, author_id))
            self.conn.commit()
            # return the new id
            rows = self.cur.fetchall()
            if len(rows) > 0:
                return rows[0][0]
            else:
                return 0
        else:
            return 0

    # updates an existing book_list record => TRUE if the record exists, FALSE if not
    def update_book(self, id, title, author_first_name, author_surname, year, isbn):
        if isinstance(id, int) and isinstance(year, int) and len(isbn) <= 13:
            self.cur.execute("UPDATE book_list SET title=%s, year=%s, isbn=%s WHERE id=%s", (title, year, isbn, id))
            self.conn.commit()
            return True
        else:
            return False

    def delete_book(self, id):
        if isinstance(id, int):
            self.cur.execute("DELETE FROM book_list WHERE id=%s", (id,))
            self.conn.commit()

# author table methods
    def get_all_authors(self):
        self.cur.execute("SELECT id, first_name, surname, photo_url, date_birth, date_death FROM author ORDER BY surname, first_name")
        rows = self.cur.fetchall()
        return rows;

    # returns author found by id
    def get_author_by_id(self, id):
        self.cur.execute("SELECT id, first_name, surname, photo_url, date_birth, date_death FROM author WHERE id=%s", (id,))
        rows = self.cur.fetchall()
        return rows

    # returns id of author record with exact match of first_name and surname
    def get_author_by_name(self, first_name, surname):
        self.cur.execute("SELECT id FROM author WHERE first_name=%s AND surname=%s ORDER BY surname, first_name LIMIT 1", (first_name, surname))
        rows = self.cur.fetchall()
        if len(rows) > 0:
            return rows[0][0]
        else:
            return 0

    # creates a new author record => id of new record
    def add_author(self, first_name, surname, photo_url, date_birth, date_death):
        if date_birth != "" and date_death != "":
            self.cur.execute("INSERT INTO author(first_name, surname, photo_url, date_birth, date_death) VALUES(%s, %s, %s, %s, %s) RETURNING id", (first_name, surname, photo_url, date_birth, date_death))
        elif date_birth != "":
            self.cur.execute("INSERT INTO author(first_name, surname, photo_url, date_birth) VALUES(%s, %s, %s, %s) RETURNING id", (first_name, surname, photo_url, date_birth))
        else:
            self.cur.execute("INSERT INTO author(first_name, surname, photo_url) VALUES(%s, %s, %s) RETURNING id", (first_name, surname, photo_url))
        self.conn.commit()
        # return the new id
        rows = self.cur.fetchall()
        if len(rows) > 0:
            return rows[0][0]
        else:
            return 0

    # updates an existing author record => TRUE if the record exists, FALSE if not
    def update_author(self, id, first_name, surname, photo_url, date_birth, date_death):
        if isinstance(id, int):
            if date_death != "":
                self.cur.execute("UPDATE author SET first_name=%s, surname=%s, photo_url=%s, date_birth=%s, date_death=%s WHERE id=%s", (first_name, surname, photo_url, date_birth, date_death, id))
            else:
                self.cur.execute("UPDATE author SET first_name=%s, surname=%s, photo_url=%s, date_birth=%s WHERE id=%s", (first_name, surname, photo_url, date_birth, id))
            self.conn.commit()
            return True
        else:
            return False

    def delete_author(self, id):
        if isinstance(id, int):
            self.cur.execute("DELETE FROM author WHERE id=%s", (id,))
            self.conn.commit()

# search methods
    # find books by title or author or year or isbn => list of books (incl author)
    def search(self, title="", author_first_name="", author_surname="", year=0, isbn=0):
        if title != "":
            title = "%" + title + "%" # for partial match
        # build sql query
        sql = """SELECT book_list.id, title, first_name, surname, year, isbn, author_id 
            FROM book_list 
            LEFT JOIN author ON book_list.author_id=author.id 
            WHERE title ILIKE %s 
            OR year=%s
            OR isbn=%s """
        if author_first_name != "" or author_surname != "":
            author_first_name = "%" + author_first_name + "%"
            author_surname = "%" + author_surname + "%"
            sql += "OR (author.first_name ILIKE %s AND author.surname ILIKE %s) "
            self.cur.execute(sql, (title, year, isbn, author_first_name, author_surname))
        else:
            self.cur.execute(sql, (title, year, isbn))
        rows = self.cur.fetchall()
        return rows;

    def get_books_by_author(self, author_id):
        self.cur.execute("SELECT book_list.id, title, first_name, surname, year, isbn, author_id FROM book_list LEFT JOIN author ON book_list.author_id=author.id WHERE author_id=%s", (author_id,))
        rows = self.cur.fetchall()
        return rows
    
    # find author by first_name or surname => list of first_name, surname tuples
    def author_lookup(self, first_name="", surname=""):
        if first_name != "":
            first_name = first_name + "%"
        if surname != "":
            surname = surname + "%"
        if first_name != "" or surname != "":
            self.cur.execute("SELECT id, first_name, surname FROM author WHERE first_name ILIKE %s OR surname ILIKE %s ORDER BY surname, first_name", (first_name, surname))
            rows = self.cur.fetchall()
            return rows
        else:
            return []

# clean up
    def __del__(self):
        self.conn.close()
