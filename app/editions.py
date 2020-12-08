from flask import make_response, request
from sqlalchemy import or_
import datetime

from app.models import Author, Book, Publisher, Edition
from app.forms import EditionForm
from app.utilities import jsonifyList, get_author_by_name

class EditionsDB:
    """ class to handle requests from api for authors """

    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
        self.headers = {"Content-Type": "application/json"}
        self.return_code_success = 200
        self.return_code_created = 201
        self.return_code_fail = 500
        self.return_code_not_found = 404

    # get all editions for given book
    def get_all(self, book_id):
        editions = Edition.query.filter(Edition.book_id==book_id)
        json = jsonifyList(editions, "editions")
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # create new edition
    def create(self, form):
        if form.validate == False:
            # return fail
            json = '{"operation":"create edition", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

        date_pub = form.date_published.data
        isbn = form.isbn.data
        book_id = form.book_id.data
        publisher_id = form.publisher_id.data
        # add the edition
        self.db.session.add(Edition(isbn=isbn, date_pub=date_pub, book_id=book_id, publisher_id=publisher_id))
        self.db.session.commit()
        # return success
        json = '{"operation":"create edition", "status":"success"}'
        return make_response(
            json,
            self.return_code_created,
            self.headers)

    # update existing edition
    def update(self, form):
        if form.validate == False or form.id.data == 0:
            # return fail
            json = '{"id":' + str(form.id.data) + ', "operation":"update edition", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

        id = form.id.data
        date_pub = form.date_published.data
        isbn = form.isbn.data
        book_id = form.book_id.data
        publisher_id = form.publisher_id.data
        Edition.query.filter(Edition.id==id).\
            update({"isbn":isbn, "date_pub":date_pub, "book_id":book_id, "publisher_id":publisher_id})
        self.db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"update edition", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # delete existing edition
    def delete(self, id):
        if id == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"delete", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        Edition.query.filter(Edition.id == id).delete()
        self.db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"delete", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # get specified edition
    def get(self, id):
        editions = Edition.query.filter(Edition.id == id)
        if editions.count() == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"get", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        json = editions.first().jsonify()
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # find editions by isbn
    def search(self, form):
        isbn = form.isbn.data
        if isbn == "":
            # return not found
            json = '{"operation":"get", "status":"not found"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        isbn = "%{}%".format(isbn)
        editions = Edition.query.filter( \
            Edition.isbn.like(isbn))
        json = jsonifyList(editions, "editions")
        return make_response(
            json,
            self.return_code_success,
            self.headers)
