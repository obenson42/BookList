import os
from flask import (
    Blueprint, flash, redirect, render_template, make_response, request, url_for, send_from_directory
)
from sqlalchemy import or_
import datetime

from book_list import db, cache
from book_list.models import Author, Book, Publisher, Edition
from book_list.forms import BookForm, AuthorForm, PublisherForm, EditionForm

bp = Blueprint('book_list', __name__)


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
    form = BookForm(request.form)
    if form.validate() == False:
        # return fail
        json = '{"operation":"create book", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    title = form.title.data
    year = form.year.data
    # get author by name
    author_id = form.author_id.data
    author_first_name = form.author_first_name.data
    author_surname = form.author_surname.data
    author = get_author_by_name(author_first_name, author_surname, True)
    if author != None:
        author_id = author.id
    # add the book
    db.session.add(Book(title=title, year=year, author_id=author_id))
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
    form = BookForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"id":' + str(form.id.data) + ', "operation":"update book", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    id = form.id.data
    title = form.title.data
    year = form.year.data
    # get author by name
    author_id = form.author_id.data
    author_first_name = form.author_first_name.data
    author_surname = form.author_surname.data
    author = get_author_by_name(author_first_name, author_surname, True)
    if author != None:
        author_id = author.id
    if id != 0:
        Book.query.filter(Book.id==id).\
            update({"title":title, "year":year, "author_id":author_id})
        db.session.commit()
        # chache time of this change
        cache.set('last_update_books', datetime.datetime.now())
        # return success
        json = '{"id":' + str(id) + ', "operation":"update book", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
 
# delete existing book
@bp.route('/book/', methods=['DELETE'])
def book_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        Book.query.filter(Book.id == id_num).delete()
        db.session.commit()
        # return success
        json = '{"id":' + str(id_num) + ', "operation":"delete", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + id + ', "operation":"delete", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# find books by title, year or author name
@bp.route('/books_search/', methods=['GET'])
def books_search():
    form = BookForm(request.args)
    title = form.title.data
    if title != "":
        title = "%{}%".format(title)
    year = form.year.data
    author_first_name = form.author_first_name.data
    author_surname = form.author_surname.data
    if title != "" or year != 0 or author_first_name != "" or author_surname != "":
        books = Book.query.join(Book.author).filter(or_(\
            Book.title.ilike(title), \
            Book.year == year, \
            Book.author.property.mapper.class_.first_name.ilike(author_first_name)))
        # return success
        json = jsonifyList(books, "books")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return not found
        json = '{"operation":"get", "status":"not found"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# find books by author_id
@bp.route('/books_by_author/', methods=['GET'])
def get_books_by_author():
    author_id = request.args.get('author_id')
    author_id_num = int(author_id) if (isinstance(author_id, str) and (author_id != "")) else 0
    if author_id_num > 0:
        books = Book.query.filter(Book.author_id == author_id_num)
        # return success
        json = jsonifyList(books, "books")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"author_id":' + author_id + ', "operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# find books by publisher_id
@bp.route('/books_by_publisher/', methods=['GET'])
def get_books_by_publisher():
    publisher_id = request.args.get('publisher_id')
    publisher_id_num = int(publisher_id) if (isinstance(publisher_id, str) and (publisher_id != "")) else 0
    if publisher_id_num > 0:
        books = db.session.query(Book).join(Edition, Edition.book_id==Book.id).join(Publisher, Publisher.id == Edition.publisher_id).filter(Publisher.id == publisher_id_num)
        # return success
        json = jsonifyList(books, "books")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"author_id":' + publisher_id + ', "operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
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
    form = AuthorForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"operation":"create author", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)
        
    first_name = form.first_name.data
    surname = form.surname.data
    date_birth = form.date_birth.data
    date_death = form.date_death.data
    db.session.add(Author(first_name=first_name, surname=surname, date_birth=date_birth, date_death=date_death))
    db.session.commit()
    # return success
    json = '{"operation":"create author", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)
    
# update existing author
@bp.route('/author/', methods=['PUT'])
def author_update():
    form = AuthorForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"id":' + str(form.id.data) + ', "operation":"update author", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    id = form.id.data
    first_name = form.first_name.data
    surname = form.surname.data
    date_birth = form.date_death.data
    date_death = form.date_death.data
    if id != 0:
        db.session.query(Author).filter(Author.id==id).\
            update({"first_name":first_name, "surname":surname, "date_birth":date_birth, "date_death":date_death})
        db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"update author", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + str(id) + ', "operation":"update author", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

@bp.route('/author/', methods=['DELETE'])
def author_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        db.session.execute("DELETE FROM Author WHERE id=:param", {"param": id_num})
        db.session.commit()
        # return success
        json = '{"id":' + str(id_num) + ', "operation":"delete", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + id + ', "operation":"delete", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)
    
# get specified author
@bp.route('/author/', methods=['GET'])
def author_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    authors = Author.query.filter(Author.id == id_num)
    if authors.count() > 0:
        json = authors.first().jsonify()
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return not found
        json = '{"operation":"get", "status":"not found"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# find an author by first name or surname
@bp.route('/author_search/', methods=['GET'])
def author_search():
    form = AuthorForm(request.args)
    first_name = form.first_name.data
    if first_name != "":
        first_name = "{}%".format(first_name)
    surname = form.surname.data
    if surname != "":
        surname = "{}%".format(surname)
    if first_name != "" or surname != "":
        authors = Author.query.filter(or_(Author.first_name.ilike(first_name), Author.surname.ilike(surname)))
        json = jsonifyList(authors, "authors")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return not found
        json = '{"operation":"get", "status":"not found"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
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
    form = PublisherForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"operation":"create publisher", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    name = form.name.data
    # add the publisher
    db.session.add(Publisher(name=name))
    db.session.commit()
    # return success
    json = '{"operation":"create publisher", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# update existing publisher
@bp.route('/publisher/', methods=['PUT'])
def publisher_update():
    form = PublisherForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"id":' + str(form.id.data) + ', "operation":"update publisher", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    id = form.id.data
    name = form.name.data
    if id != 0:
        Publisher.query.filter(Publisher.id==id_num).\
            update({"name":name})
        db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"update publisher", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + str(id) + ', "operation":"update publisher", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# delete existing publisher
@bp.route('/publisher/', methods=['DELETE'])
def publisher_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        Publisher.query.filter(Publisher.id == id_num).delete()
        db.session.commit()
        # return succcess
        json = '{"id":' + str(id_num) + ', "operation":"delete", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + id + ', "operation":"delete", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# get specified publisher
@bp.route('/publisher/', methods=['GET'])
def publisher_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    publishers = Publisher.query.filter(Publisher.id == id_num)
    if publishers.count() > 0:
        json = publishers.first().jsonify()
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + id + ', "operation":"get", "status":"not found"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# find publishers by title, year or author name
@bp.route('/publisher_search/', methods=['GET'])
def publisher_search():
    form = PublisherForm(request.args)
    name = form.name.data
    if name != "":
        name = "%{}%".format(name)
        publishers = Publisher.query.filter( \
            Publisher.name.ilike(name))
        json = jsonifyList(publishers, "publishers")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return not found
        json = '{"operation":"get", "status":"not found"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

## edition routes
# get all editions for given book
@bp.route('/editions/', methods=['GET'])
def get_all_editions():
    book_id = request.args.get('book_id')
    book_id_num = int(book_id) if (isinstance(book_id, str) and (book_id != "")) else 0
    editions = Edition.query.filter(Edition.book_id==book_id_num)
    #editions = Edition.query.all()
    json = jsonifyList(editions, "editions")
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# create new edition
@bp.route('/edition/', methods=['PUSH'])
def edition_create():
    form = EditionForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"operation":"create edition", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    date_pub = form.date_published.data
    isbn = form.isbn.data
    book_id = form.book_id.data
    publisher_id = form.publisher_id.data
    # add the edition
    db.session.add(Edition(isbn=isbn, date_pub=date_pub, book_id=book_id, publisher_id=publisher_id))
    db.session.commit()
    # return success
    json = '{"operation":"create edition", "status":"success"}'
    headers = {"Content-Type": "application/json"}
    return make_response(
        json,
        200,
        headers)

# update existing edition
@bp.route('/edition/', methods=['PUT'])
def edition_update():
    form = EditionForm(request.form)
    if form.validate == False:
        # return fail
        json = '{"id":' + str(form.id.data) + ', "operation":"update edition", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            500,
            headers)

    id = form.id.data
    date_pub = form.date_published.data
    isbn = form.isbn.data
    book_id = form.book_id.data
    publisher_id = form.publisher_id.data
    if id != 0:
        Edition.query.filter(Edition.id==id).\
            update({"isbn":isbn, "date_pub":date_pub, "book_id":book_id, "publisher_id":publisher_id})
        db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"update edition", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return dail
        json = '{"id":' + str(id) + ', "operation":"update edition", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# delete existing edition
@bp.route('/edition/', methods=['DELETE'])
def edition_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    if id_num > 0:
        Edition.query.filter(Edition.id == id_num).delete()
        db.session.commit()
        # return success
        json = '{"id":' + str(id_num) + ', "operation":"delete", "status":"success"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + id + ', "operation":"delete", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# get specified edition
@bp.route('/edition/', methods=['GET'])
def edition_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    editions = Edition.query.filter(Edition.id == id_num)
    if editions.count() > 0:
        json = editions.first().jsonify()
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return fail
        json = '{"id":' + id + ', "operation":"get", "status":"fail"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
            headers)

# find editions by isbn
@bp.route('/editions_search/', methods=['GET'])
def editions_search():
    form = EditionForm(request.args)
    isbn = form.isbn.data
    if isbn != "":
        isbn = "%{}%".format(isbn)
        editions = Edition.query.filter( \
            Edition.isbn.like(isbn))
        json = jsonifyList(editions, "editions")
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            200,
            headers)
    else:
        # return not found
        json = '{"operation":"get", "status":"not found"}'
        headers = {"Content-Type": "application/json"}
        return make_response(
            json,
            404,
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
