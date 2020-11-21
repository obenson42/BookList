import os
from flask import Flask, render_template, make_response, request
import urllib.parse as urlparse
from urllib.parse import parse_qs
import datetime
from book_list_back import Database

class FrontEnd:
    """ class to intermediate between web service methods and the database object """

    def __init__(self, db):
        self.db = db

# book methods
    def get_all_books(self):
        rows = []
        if self.db != None:
            rows = self.db.get_all_books()
        # return results as JSON
        return self.book_list_to_json(rows)

    def add_book(self, title, author_first_name, author_surname, year_num, isbn):
        return self.db.add_book(title, author_first_name, author_surname, year_num, isbn)

    def update_book(self, id, title, author_first_name, author_surname, year_num, isbn):
        if id != 0:
            return self.db.update_book(id, title, author_first_name, author_surname, year_num, isbn)
        else:
            return 0

    def delete_book(self, id):
        if id != 0:
            return self.db.delete_book(id)
        else:
            return 0

# author methods
    def get_all_authors(self):
        rows = []
        if self.db != None:
            rows = self.db.get_all_authors()
        # return results as JSON
        return self.author_list_to_json(rows)

    def get_author_by_id(self, id):
        rows = self.db.get_author_by_id(id)
        if len(rows) > 0:
            # return results as JSON
            return '{"id":' + str(rows[0][0]) + ', "first_name":"' + rows[0][1] + '", "surname":"' + rows[0][2] + '"}'
        else:
            return '{}'

    def add_author(self, first_name, surname, photo_url, date_birth, date_death):
        return self.db.add_author(first_name, surname, photo_url, date_birth, date_death)

    def update_author(self, id, first_name, surname, photo_url, date_birth, date_death):
        if id != 0:
            return self.db.update_author(id, first_name, surname, photo_url, date_birth, date_death)
        else:
            return 0

    def delete_author(self, id):
        if id != 0:
            return self.db.delete_author(id)
        else:
            return 0

# search methods
    # find books by title or author or year or isbn => JSON array of books (incl author)
    def search(self, title, author_first_name, author_surname, year_num, isbn):
        rows = self.db.search(title, author_first_name, author_surname, year_num, isbn)
        # return results as JSON
        return self.book_list_to_json(rows)

    # find books by author_id
    def get_books_by_author(self, author_id):
        rows = self.db.get_books_by_author(author_id)
        # return results as JSON
        return self.book_list_to_json(rows)

    # find author by first_name or surname => JSON array of authors
    def author_lookup(self, first_name, surname):
        rows = self.db.author_lookup(first_name, surname)
        # only want to return the first entry
        if len(rows) > 0:
            # return results as JSON
            return '{"id":' + str(rows[0][0]) + ', "first_name":"' + rows[0][1] + '", "surname":"' + rows[0][2] + '"}'
        else:
            return '{}'

# convert db response to JSON
    def book_list_to_json(self, rows):
        json = ''
        for row in rows:
            json += '{"id":' + str(row[0])
            json += ',"title":"' + row[1] + '"'
            json += ',"author_first_name":"' + (str(row[2]) if isinstance(row[2], str) else "") + '"'
            json += ',"author_surname":"' + (str(row[3]) if isinstance(row[3], str) else "") + '"'
            json += ',"year":' + str(row[4])
            json += ',"isbn":"' + row[5].strip() + '"'
            json += ',"author_id":' + (str(row[6]) if isinstance(row[6], int) else "0")
            json += '},'
        json = json[:-1] # remove trailing comma
        json = '{"books":[' + json + ']}'
        return json

    def author_list_to_json(self, rows):
        json = ''
        for row in rows:
            json += '{"id":' + str(row[0])
            json += ',"first_name":"' + (str(row[1]) if isinstance(row[1], str) else "") + '"'
            json += ',"surname":"' + (str(row[2]) if isinstance(row[2], str) else "") + '"'
            json += ',"photo_url":"' + (str(row[3]) if isinstance(row[3], str) else "") + '"'
            json += ',"date_birth":"' + (str(row[4]) if isinstance(row[4], datetime.date) else "") + '"'
            json += ',"date_death":"' + (str(row[5]) if isinstance(row[5], datetime.date) else "") + '"'
            json += '},'
        json = json[:-1] # remove trailing comma
        return '{"authors":[' + json + ']}'

if 'DATABASE_URL' in os.environ:
    db = Database(os.environ['DATABASE_URL'], 'require')
else:
    db = Database("dbname='store' user='postgres' password='postgres123' host='localhost' port='5433'", 'allow')
booklist = FrontEnd(db)

def create_app():
    app=Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key'
    )
    return app

create_app()

@app.route('/')
def home():
    html = render_template("home.html")
    return html

## API for Single Page Application
## all of these requests return JSON

## book routes
# get all books (incl author)
@app.route('/books/', methods=['GET'])
def get_all_books():
    json = booklist.get_all_books()
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# get books for specific author
@app.route('/books_by_author/', methods=['GET'])
def books_by_author():
    author_id = request.args.get('author_id')
    author_id_num = int(author_id) if (isinstance(author_id, str) and (author_id != "")) else 0
    json = booklist.get_books_by_author(author_id_num)
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# find books
@app.route('/search/', methods=['GET'])
def search():
    title = request.args.get('title')
    author_first_name = request.args.get('author_first_name')
    author_surname = request.args.get('author_surname')
    year = request.args.get('year')
    year_num = int(year) if (isinstance(year, str) and (year != "")) else 0
    isbn = request.args.get('isbn')
    json = booklist.search(title, author_first_name, author_surname, year_num, isbn)
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new book
@app.route('/book/', methods=['PUSH'])
def book_create():
    status = 0
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    title = request.form.get('title')
    author_first_name = request.form.get('author_first_name')
    author_surname = request.form.get('author_surname')
    year = request.form.get('year')
    year_num = int(year) if (isinstance(year, str) and (year != "")) else 0
    isbn = request.form.get('isbn')
    if id_num == 0:
        id_num = booklist.add_book(title, author_first_name, author_surname, year_num, isbn)
        success = (id_num != 0)
    if success:
        json = '{"id":' + str(id_num) + ', "operation":"create book", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"create book", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)
    
# update existing book
@app.route('/book/', methods=['PUT'])
def book_update():
    status = 0
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    title = request.form.get('title')
    author_first_name = request.form.get('author_first_name')
    author_surname = request.form.get('author_surname')
    year = request.form.get('year')
    year_num = int(year) if (isinstance(year, str) and (year != "")) else 0
    isbn = request.form.get('isbn')
    if id_num != 0:
        success = booklist.update_book(id_num, title, author_first_name, author_surname, year_num, isbn)
    if success:
        json = '{"id":' + str(id_num) + ', "operation":"update book", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"update book", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

@app.route('/book/', methods=['DELETE'])
def book_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        booklist.delete_book(id_num);
        json = '{"id":' + str(id_num) + ', "operation":"delete", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"delete", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

## author routes
# get all authors
@app.route('/authors/', methods=['GET'])
def get_all_authors():
    json = booklist.get_all_authors()
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# find an author by id
@app.route('/author/', methods=['GET'])
def get_author_by_id():
    id = request.args.get('id')
    json = booklist.get_author_by_id(id)
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# find an author by first name or surname
@app.route('/author_by_name/', methods=['GET'])
def get_author_by_name():
    first_name = request.args.get('first_name')
    surname = request.args.get('surname')
    json = booklist.author_lookup(first_name, surname)
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new book
@app.route('/author/', methods=['PUSH'])
def author_create():
    status = 0
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    photo_url = request.form.get('photo_url')
    date_birth = request.form.get('date_birth')
    date_death = request.form.get('date_death')
    if id_num == 0:
        id_num = booklist.add_author(first_name, surname, photo_url, date_birth, date_death)
        success = (id_num != 0)
    if success:
        json = '{"id":' + str(id_num) + ', "operation":"create author", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"create author", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)
    
# update existing book
@app.route('/author/', methods=['PUT'])
def author_update():
    status = 0
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    photo_url = request.form.get('photo_url')
    date_birth = request.form.get('date_birth')
    date_death = request.form.get('date_death')
    if id_num != 0:
        success = booklist.update_author(id_num, first_name, surname, photo_url, date_birth, date_death)
    if success:
        json = '{"id":' + str(id_num) + ', "operation":"update author", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"update author", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

@app.route('/author/', methods=['DELETE'])
def author_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        booklist.delete_author(id_num);
        json = '{"id":' + str(id_num) + ', "operation":"delete", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"delete", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(debug=True)
