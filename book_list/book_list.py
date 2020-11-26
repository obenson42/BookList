from flask import (
    Blueprint, flash, redirect, render_template, make_response, request, url_for, send_from_directory
)
from sqlalchemy import or_
import datetime

from book_list import db, cache
from book_list.models import Author, Book, Publisher, Edition

#from book_list_web import FrontEnd

bp = Blueprint('book_list', __name__)
#booklist = FrontEnd(db)

@bp.route('/')
def home():
    html = render_template("home.html")
    return html

## API for Single Page Application
## all of these requests return JSON

## book routes
# get all books (incl author)
@bp.route('/books/', methods=['GET'])
def get_all_books():
    books = Book.query.all()
    json = jsonifyList(books, "books")
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new book
@bp.route('/book/', methods=['PUSH'])
def book_create():
    title = request.form.get('title')
    year = request.form.get('year')
    year_num = int(year) if (isinstance(year, str) and (year != "")) else 0
    # get author by name
    author_id = 0
    author_first_name = request.form.get('author_first_name')
    author_surname = request.form.get('author_surname')
    author = get_author_by_name(author_first_name, author_surname, True)
    if author != None:
        author_id = author.id
    # add the book
    db.session.add(Book(title=title, year=year_num, author_id=author_id))
    db.session.commit()
    # chache time of this change
    cache.set('last_update_books', datetime.datetime.now())
    # return success
    json = '{"operation":"create book", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# update existing book
@bp.route('/book/', methods=['PUT'])
def book_update():
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    title = request.form.get('title')
    year = request.form.get('year')
    year_num = int(year) if (isinstance(year, str) and (year != "")) else 0
    # get author by name
    author_id = 0
    author_first_name = request.form.get('author_first_name')
    author_surname = request.form.get('author_surname')
    author = get_author_by_name(author_first_name, author_surname, True)
    if author != None:
        author_id = author.id
    if id_num != 0:
        Book.query.filter(Book.id==id_num).\
            update({"title":title, "year":year_num, "author_id":author_id})
        db.session.commit()
        # chache time of this change
        cache.set('last_update_books', datetime.datetime.now())
        # return success
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

# delete existing book
@bp.route('/book/', methods=['DELETE'])
def book_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        Book.query.filter(Book.id == id_num).delete()
        db.session.commit()
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

# find books by title, year or author name
@bp.route('/books_search/', methods=['GET'])
def books_search():
    title = request.args.get('title')
    if title != "":
        title = "%" + title + "%"
    year = request.args.get('year')
    year_num = int(year) if (isinstance(year, str) and (year != "")) else 0
    author_first_name = request.args.get('author_first_name')
    author_surname = request.args.get('author_surname')
    if title != "" or year != "" or author_first_name != "" or author_surname != "":
        books = Book.query.join(Book.author).filter(or_(\
            Book.title.ilike(title), \
            Book.year == year_num, \
            Book.author.property.mapper.class_.first_name.ilike(author_first_name)))
        json = jsonifyList(books, "books")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

# find books by author_id
@bp.route('/books_by_author/', methods=['GET'])
def get_books_by_author():
    author_id = request.args.get('author_id')
    author_id_num = int(author_id) if (isinstance(author_id, str) and (author_id != "")) else 0
    if author_id_num > 0:
        books = Book.query.filter(Book.author_id == author_id_num)
        json = jsonifyList(books, "books")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"author_id":' + author_id + ', "operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

# find books by publisher_id
@bp.route('/books_by_publisher/', methods=['GET'])
def get_books_by_publisher():
    publisher_id = request.args.get('publisher_id')
    publisher_id_num = int(publisher_id) if (isinstance(publisher_id, str) and (publisher_id != "")) else 0
    if publisher_id_num > 0:
        books = Book.query.join(Book.edition).join(Edition.publisher).filter(Publisher.id == publisher_id_num)
        json = jsonifyList(books, "books")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"author_id":' + author_id + ', "operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

## author routes
# get all authors
@bp.route('/authors/', methods=['GET'])
def get_all_authors():
    authors = Author.query.all()
    json = jsonifyList(authors, "authors")
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new author
@bp.route('/author/', methods=['PUSH'])
def author_create():
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    date_birth = datetime.date.fromisoformat(request.form.get('date_birth')) if request.form.get('date_birth') != "" else None
    date_death = datetime.date.fromisoformat(request.form.get('date_death')) if request.form.get('date_death') != "" else None
    db.session.add(Author(first_name=first_name, surname=surname, date_birth=date_birth, date_death=date_death))
    db.session.commit()
    json = '{"operation":"create author", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)
    
# update existing author
@bp.route('/author/', methods=['PUT'])
def author_update():
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    date_birth = datetime.date.fromisoformat(request.form.get('date_birth')) if request.form.get('date_birth') != "" else None
    date_death = datetime.date.fromisoformat(request.form.get('date_death')) if request.form.get('date_death') != "" else None
    if id_num != 0:
        db.session.query(Author).filter(Author.id==id_num).\
            update({"first_name":first_name, "surname":surname, "date_birth":date_birth, "date_death":date_death})
        db.session.commit()
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

@bp.route('/author/', methods=['DELETE'])
def author_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        db.session.execute("DELETE FROM Author WHERE id=:param", {"param": id_num})
        db.session.commit()
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
    
# get specified author
@bp.route('/author/', methods=['GET'])
def author_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    authors = Author.query.filter(Author.id == id_num)
    json = authors.first().jsonify()
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# find an author by first name or surname
@bp.route('/author_search/', methods=['GET'])
def author_search():
    first_name = request.args.get('first_name')
    if first_name != "":
        first_name = "{}%".format(first_name)
    surname = request.args.get('surname')
    if surname != "":
        surname = "{}%".format(surname)
    authors = Author.query.filter(or_(Author.first_name.ilike(first_name), Author.surname.ilike(surname)))
    json = jsonifyList(authors, "authors")
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

## publisher routes
# get all publishers (incl author)
@bp.route('/publishers/', methods=['GET'])
def get_all_publishers():
    publishers = Publisher.query.all()
    json = jsonifyList(publishers, "publishers")
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new publisher
@bp.route('/publisher/', methods=['PUSH'])
def publisher_create():
    name = request.form.get('name')
    # add the publisher
    db.session.add(Publisher(name=name))
    db.session.commit()
    json = '{"operation":"create publisher", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# update existing publisher
@bp.route('/publisher/', methods=['PUT'])
def publisher_update():
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    name = request.form.get('name')
    if id_num != 0:
        Publisher.query.filter(Publisher.id==id_num).\
            update({"name":name})
        db.session.commit()
        json = '{"id":' + str(id_num) + ', "operation":"update publisher", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"update publisher", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

# delete existing publisher
@bp.route('/publisher/', methods=['DELETE'])
def publisher_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        Publisher.query.filter(Publisher.id == id_num).delete()
        db.session.commit()
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

# get specified publisher
@bp.route('/publisher/', methods=['GET'])
def publisher_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    publishers = Publisher.query.filter(Publisher.id == id_num)
    json = publishers.first().jsonify()
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# find publishers by title, year or author name
@bp.route('/publishers_search/', methods=['GET'])
def publishers_search():
    name = request.args.get('name')
    if name != "":
        name = "%" + name + "%"
    if name != "":
        publishers = Publisher.query.filter( \
            Publisher.name.ilike(name))
        json = jsonifyList(publishers, "publishers")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

## edition routes
# get all editions (incl author)
@bp.route('/editions/', methods=['GET'])
def get_all_editions():
    editions = Edition.query.all()
    json = jsonifyList(editions, "editions")
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new edition
@bp.route('/edition/', methods=['PUSH'])
def edition_create():
    date_pub = datetime.date.fromisoformat(request.form.get('date_pub')) if request.form.get('date_pub') != "" else None
    isbn = request.form.get('isbn')
    # add the edition
    db.session.add(Edition(isbn=isbn, date_pub=date_pub))
    db.session.commit()
    json = '{"operation":"create edition", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# update existing edition
@bp.route('/edition/', methods=['PUT'])
def edition_update():
    id = request.form.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    date_pub = datetime.date.fromisoformat(request.form.get('date_pub')) if request.form.get('date_pub') != "" else None
    isbn = request.form.get('isbn')
    book_id = request.form.get('book_id')
    publisher_id = request.form.get('publisher_id')
    if id_num != 0:
        Edition.query.filter(Edition.id==id_num).\
            update({"isbn":isbn, "date_pub":date_pub, "book_id":book_id, "publisher_id":publisher_id})
        db.session.commit()
        json = '{"id":' + str(id_num) + ', "operation":"update edition", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"id":' + id + ', "operation":"update edition", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

# delete existing edition
@bp.route('/edition/', methods=['DELETE'])
def edition_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        Edition.query.filter(Edition.id == id_num).delete()
        db.session.commit()
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

# get specified edition
@bp.route('/edition/', methods=['GET'])
def edition_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    editions = Edition.query.filter(Edition.id == id_num)
    json = editions.first().jsonify()
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# find editions isbn
@bp.route('/editions_search/', methods=['GET'])
def editions_search():
    isbn = request.args.get('isbn')
    if isbn != "":
        isbn = "%" + isbn + "%"
    if isbn != "":
        editions = Edition.query.filter( \
            Edition.isbn.like(isbn))
        json = jsonifyList(editions, "editions")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        json = '{"operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

### extra routes
@bp.route('/last_update_books/')
def last_update_books():
    last_update = cache.get('last_update_books')
    if last_update != None:
        last_update = last_update.isoformat()
    json = '{ "last_update": "%s" }' % (last_update,)
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

@bp.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


## utilities
# find an author by name, create if it doesn't exist
def get_author_by_name(first_name, surname, create):
    authors = Author.query.filter(Author.first_name==first_name, Author.surname==surname)
    if authors.count() > 0:
        return authors.first()
    elif create==True:
        author = Author(first_name=first_name, surname=surname)
        db.session.add(author)
        db.session.commit()
        return author
    else:
        return None

# convert to JSON functions
def jsonifyList(list, name):
    json = ""
    for obj in list:
        json += obj.jsonify() + ","
    json = json[:-1] # remove trailing comma
    json = '{"%s":[%s]}' % (name, json)
    return json
