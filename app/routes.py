import os
basedir = os.path.abspath(os.path.dirname(__file__))

import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, make_response, request, session, url_for, send_from_directory
)
from flask_login import login_required
from flask_cors import CORS

from sqlalchemy import or_
import datetime

from app import db, cache
from app.models import User, Author, Book, Publisher, Edition
from app.forms import BookForm, AuthorForm, PublisherForm, EditionForm
from app.books import BooksDB
from app.authors import AuthorsDB
from app.publishers import PublishersDB
from app.editions import EditionsDB

from app.utilities import get_author_by_name

bp = Blueprint('main', __name__)
booksDB = BooksDB(db, cache)
authorsDB = AuthorsDB(db, cache)
publishersDB = PublishersDB(db, cache)
editionsDB = EditionsDB(db, cache)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    html = render_template("home.html")
    return html

## API for Single Page Application
## all of these requests return JSON

## book routes
# get all books (incl author)
@bp.route('/books/', methods=['GET'])
@login_required
def get_all_books():
    return booksDB.get_all()

# create new book
@bp.route('/book/', methods=['PUSH'])
@login_required
def book_create():
    form = BookForm(request.form)
    return booksDB.create(form)

# update existing book
@bp.route('/book/', methods=['PUT'])
@login_required
def book_update():
    form = BookForm(request.form)
    return booksDB.update(form)
 
# delete existing book
@bp.route('/book/<int:id>', methods=['DELETE'])
@login_required
def book_delete(id):
    return booksDB.delete(id)

# find books by title, year or author name
@bp.route('/books_search/', methods=['GET'])
@login_required
def books_search():
    form = BookForm(request.args)
    return booksDB.search(form)

# find books by author_id
@bp.route('/books_by_author/<int:author_id>', methods=['GET'])
@login_required
def get_books_by_author(author_id):
    return booksDB.get_by_author(author_id)

# find books by publisher_id
@bp.route('/books_by_publisher/<int:publisher_id>', methods=['GET'])
@login_required
def get_books_by_publisher(publisher_id):
    return booksDB.get_by_publisher(publisher_id)

## author routes
# get all authors
@bp.route('/authors/', methods=['GET'])
@login_required
def get_all_authors():
    return authorsDB.get_all()

# create new author
@bp.route('/author/', methods=['PUSH'])
@login_required
def author_create():
    form = AuthorForm(request.form)
    return authorsDB.create(form)
    
# update existing author
@bp.route('/author/', methods=['PUT'])
@login_required
def author_update():
    form = AuthorForm(request.form)
    return authorsDB.update(form)

@bp.route('/author/<int:id>', methods=['DELETE'])
@login_required
def author_delete(id):
    return authorsDB.delete(id)
    
# get specified author
@bp.route('/author/<int:id>', methods=['GET'])
@login_required
def author_get(id):
    return authorsDB.get(id)

# find an author by first name or surname
@bp.route('/author_search/', methods=['GET'])
@login_required
def author_search():
    form = AuthorForm(request.args)
    return authorsDB.search(form)

## publisher routes
# get all publishers (incl author)
@bp.route('/publishers/', methods=['GET'])
@login_required
def get_all_publishers():
    return publishersDB.get_all()

# create new publisher
@bp.route('/publisher/', methods=['PUSH'])
@login_required
def publisher_create():
    form = PublisherForm(request.form)
    return publishersDB.create(form)

# update existing publisher
@bp.route('/publisher/', methods=['PUT'])
@login_required
def publisher_update():
    form = PublisherForm(request.form)
    return publishersDB.update(form)

# delete existing publisher
@bp.route('/publisher/<int:id>', methods=['DELETE'])
@login_required
def publisher_delete(id):
    return publishersDB.delete(id)

# get specified publisher
@bp.route('/publisher/<int:id>', methods=['GET'])
@login_required
def publisher_get(id):
    return publishersDB.get(id)

# find publishers by title, year or author name
@bp.route('/publisher_search/', methods=['GET'])
@login_required
def publisher_search():
    form = PublisherForm(request.args)
    return publishersDB.search(form)

## edition routes
# get all editions for given book
@bp.route('/editions/<int:book_id>', methods=['GET'])
@login_required
def get_all_editions(book_id):
    return editionsDB.get_all(book_id)

# create new edition
@bp.route('/edition/', methods=['PUSH'])
@login_required
def edition_create():
    form = EditionForm(request.form)
    return editionsDB.create(form)

# update existing edition
@bp.route('/edition/', methods=['PUT'])
@login_required
def edition_update():
    form = EditionForm(request.form)
    return editionsDB.update(form)

# delete existing edition
@bp.route('/edition/<int:id>', methods=['DELETE'])
@login_required
def edition_delete(id):
    return editionsDB.delete(id)

# get specified edition
@bp.route('/edition/<int:id>', methods=['GET'])
@login_required
def edition_get(id):
    return editionsDB.get(id)

# find editions by isbn
@bp.route('/editions_search/', methods=['GET'])
@login_required
def editions_search():
    form = EditionForm(request.args)
    return editionsDB.search(form)

### extra routes
# return date/time of last update to the books db
@bp.route('/last_update_books/')
@login_required
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
    return send_from_directory(os.path.join(basedir, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
