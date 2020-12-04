from flask import make_response
from sqlalchemy import or_
import datetime

from book_list.models import Author, Book, Publisher, Edition
from book_list.forms import BookForm
from book_list.utilities import jsonifyList, get_author_by_name

class BooksDB:
    """ class to handle requests from api for books """

    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
        self.headers = {"Content-Type": "application/json"}
        self.return_code_success = 200
        self.return_code_fail = 500
        self.return_code_not_found = 404

    # get all books (incl author) => JSON dictionary of book dictionaries
    def get_all(self):
        books = Book.query.all()
        json = jsonifyList(books, "books")
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # create new book => JSON dictionary with success or fail status
    def create(self, form):
        if form.validate() == False:
            # return fail
            json = '{"operation":"create book", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

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
        self.db.session.add(Book(title=title, year=year, author_id=author_id))
        self.db.session.commit()
        # chache time of this change
        self.cache.set('last_update_books', datetime.datetime.now())
        # return success
        json = '{"operation":"create book", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # update existing book => JSON dictionary with success or fail status
    def update(self, form):
        if form.validate == False or form.id.data == 0:
            # return fail
            json = '{"id":' + str(form.id.data) + ', "operation":"update book", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

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
        Book.query.filter(Book.id==id).\
            update({"title":title, "year":year, "author_id":author_id})
        self.db.session.commit()
        # chache time of this change
        self.cache.set('last_update_books', datetime.datetime.now())
        # return success
        json = '{"id":' + str(id) + ', "operation":"update book", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)
 
    # delete existing book => JSON dictionary with success or fail status
    def delete(self, id):
        if id == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"delete", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        Book.query.filter(Book.id == id).delete()
        self.db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"delete", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # find books by title, year or author name => JSON dictionary of book dictionaries
    def search(self, form):
        title = form.title.data
        if title != "":
            title = "%{}%".format(title)
        year = form.year.data
        author_first_name = form.author_first_name.data
        author_surname = form.author_surname.data
        if title == "" and year == 0 and author_first_name == "" and author_surname == "":
            # return not found
            json = '{"operation":"get", "status":"not found"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        books = Book.query.join(Book.author).filter(or_(\
            Book.title.ilike(title), \
            Book.year == year, \
            Book.author.property.mapper.class_.first_name.ilike(author_first_name)))
        # return success
        json = jsonifyList(books, "books")
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # find books by author_id => JSON dictionary of book dictionaries
    def get_by_author(self, author_id):
        if author_id == 0:
            # return fail
            json = '{"author_id":' + str(author_id) + ', "operation":"get", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        books = Book.query.filter(Book.author_id == author_id)
        # return success
        json = jsonifyList(books, "books")
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # find books by publisher_id => JSON dictionary of book dictionaries
    def get_by_publisher(self, publisher_id):
        if publisher_id == 0:
            # return fail
            json = '{"author_id":' + str(publisher_id) + ', "operation":"get", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        books = self.db.session.query(Book). \
            join(Edition, Edition.book_id==Book.id). \
            join(Publisher, Publisher.id == Edition.publisher_id). \
            filter(Publisher.id == publisher_id)
        # return success
        json = jsonifyList(books, "books")
        return make_response(
            json,
            self.return_code_success,
            self.headers)
