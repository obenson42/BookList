import os
from flask import (
    Blueprint, flash, redirect, render_template, make_response, request, url_for, send_from_directory
)
from sqlalchemy import or_
import datetime

from book_list import db, cache
from book_list.models import Author, Book, Publisher, Edition
from book_list.forms import BookForm, AuthorForm, PublisherForm, EditionForm
from book_list.books import BooksDB
from book_list.authors import AuthorsDB
from book_list.publishers import PublishersDB
from book_list.editions import EditionsDB

from book_list.utilities import jsonifyList, get_author_by_name

bp = Blueprint('book_list', __name__)
booksDB = BooksDB(db, cache)
authorsDB = AuthorsDB(db, cache)
publishersDB = PublishersDB(db, cache)
editionsDB = EditionsDB(db, cache)

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
    return booksDB.get_all()

# create new book
@bp.route('/book/', methods=['PUSH'])
def book_create():
    form = BookForm(request.form)
    return booksDB.create(form)

# update existing book
@bp.route('/book/', methods=['PUT'])
def book_update():
    form = BookForm(request.form)
    return booksDB.update(form)
 
# delete existing book
@bp.route('/book/', methods=['DELETE'])
def book_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return booksDB.delete(id_num)

# find books by title, year or author name
@bp.route('/books_search/', methods=['GET'])
def books_search():
    form = BookForm(request.args)
    return booksDB.search(form)

# find books by author_id
@bp.route('/books_by_author/', methods=['GET'])
def get_books_by_author():
    author_id = request.args.get('author_id')
    author_id_num = int(author_id) if (isinstance(author_id, str) and (author_id != "")) else 0
    return booksDB.get_by_author(author_id_num)

# find books by publisher_id
@bp.route('/books_by_publisher/', methods=['GET'])
def get_books_by_publisher():
    publisher_id = request.args.get('publisher_id')
    publisher_id_num = int(publisher_id) if (isinstance(publisher_id, str) and (publisher_id != "")) else 0
    return booksDB.get_by_publisher(publisher_id_num)

## author routes
# get all authors
@bp.route('/authors/', methods=['GET'])
def get_all_authors():
    return authorsDB.get_all()

# create new author
@bp.route('/author/', methods=['PUSH'])
def author_create():
    form = AuthorForm(request.form)
    return authorsDB.create(form)
    
# update existing author
@bp.route('/author/', methods=['PUT'])
def author_update():
    form = AuthorForm(request.form)
    return authorsDB.update(form)

@bp.route('/author/', methods=['DELETE'])
def author_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return authorsDB.delete(id_num)
    
# get specified author
@bp.route('/author/', methods=['GET'])
def author_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return authorsDB.get(id_num)

# find an author by first name or surname
@bp.route('/author_search/', methods=['GET'])
def author_search():
    form = AuthorForm(request.args)
    return authorsDB.search(form)

## publisher routes
# get all publishers (incl author)
@bp.route('/publishers/', methods=['GET'])
def get_all_publishers():
    return publishersDB.get_all()

# create new publisher
@bp.route('/publisher/', methods=['PUSH'])
def publisher_create():
    form = PublisherForm(request.form)
    return publishersDB.create(form)

# update existing publisher
@bp.route('/publisher/', methods=['PUT'])
def publisher_update():
    form = PublisherForm(request.form)
    return publishersDB.update(form)

# delete existing publisher
@bp.route('/publisher/', methods=['DELETE'])
def publisher_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return publishersDB.delete(id_num)

# get specified publisher
@bp.route('/publisher/', methods=['GET'])
def publisher_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return publishersDB.get(id)

# find publishers by title, year or author name
@bp.route('/publisher_search/', methods=['GET'])
def publisher_search():
    form = PublisherForm(request.args)
    return publishersDB.search(form)

## edition routes
# get all editions for given book
@bp.route('/editions/', methods=['GET'])
def get_all_editions():
    book_id = request.args.get('book_id')
    book_id_num = int(book_id) if (isinstance(book_id, str) and (book_id != "")) else 0
    return editionsDB.get_all(book_id_num)

# create new edition
@bp.route('/edition/', methods=['PUSH'])
def edition_create():
    form = EditionForm(request.form)
    return editionsDB.create(form)

# update existing edition
@bp.route('/edition/', methods=['PUT'])
def edition_update():
    form = EditionForm(request.form)
    return editionsDB.update(form)

# delete existing edition
@bp.route('/edition/', methods=['DELETE'])
def edition_delete():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return editionsDB.delete(id_num)

# get specified edition
@bp.route('/edition/', methods=['GET'])
def edition_get():
    id = request.args.get('id')
    id_num = int(id) if (isinstance(id, str) and (id != "")) else 0
    return editionsDB.get(id_num)

# find editions by isbn
@bp.route('/editions_search/', methods=['GET'])
def editions_search():
    form = EditionForm(request.args)
    return editionsDB.search(form)

### extra routes
# return date/time of last update to the books db
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
