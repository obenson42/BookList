from flask import make_response
from sqlalchemy import or_
import datetime

from app.models import Author, Book, Publisher, Edition
from app.forms import PublisherForm
from app.utilities import jsonifyList, get_author_by_name

class PublishersDB:
    """ class to handle requests from api for authors """

    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
        self.headers = {"Content-Type": "application/json"}
        self.return_code_success = 200
        self.return_code_created = 201
        self.return_code_fail = 500
        self.return_code_not_found = 404

    # get all publishers (incl author)
    def get_all(self):
        publishers = Publisher.query.all()
        json = jsonifyList(publishers, "publishers")
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # create new publisher
    def create(self, form):
        if form.validate == False:
            # return fail
            json = '{"operation":"create publisher", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

        name = form.name.data
        # add the publisher
        self.db.session.add(Publisher(name=name))
        self.db.session.commit()
        # return success
        json = '{"operation":"create publisher", "status":"success"}'
        return make_response(
            json,
            self.return_code_created,
            self.headers)

    # update existing publisher
    def update(self, form):
        if form.validate == False or form.id.data == 0:
            # return fail
            json = '{"id":' + str(form.id.data) + ', "operation":"update publisher", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

        id = form.id.data
        name = form.name.data
        Publisher.query.filter(Publisher.id==id).\
            update({"name":name})
        self.db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"update publisher", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # delete existing publisher
    def delete(self, id):
        if id == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"delete", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        Publisher.query.filter(Publisher.id == id).delete()
        self.db.session.commit()
        # return succcess
        json = '{"id":' + str(id) + ', "operation":"delete", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # get specified publisher
    def get(self, id):
        publishers = Publisher.query.filter(Publisher.id == id)
        if publishers.count() == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"get", "status":"not found"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        else:
            json = publishers.first().jsonify()
            return make_response(
                json,
                self.return_code_success,
                self.headers)

    # find publishers by title, year or author name
    def search(self, form):
        name = form.name.data
        if name == "":
            # return not found
            json = '{"operation":"get", "status":"not found"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        name = "%{}%".format(name)
        publishers = Publisher.query.filter( \
            Publisher.name.ilike(name))
        json = jsonifyList(publishers, "publishers")
        return make_response(
            json,
            self.return_code_success,
            self.headers)
