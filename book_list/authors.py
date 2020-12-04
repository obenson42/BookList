from flask import make_response
from sqlalchemy import or_
import datetime

from book_list.models import Author, Book, Publisher, Edition
from book_list.forms import AuthorForm
from book_list.utilities import jsonifyList, get_author_by_name

class AuthorsDB:
    """ class to handle requests from api for authors """

    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
        self.headers = {"Content-Type": "application/json"}
        self.return_code_success = 200
        self.return_code_fail = 500
        self.return_code_not_found = 404

    # get all authors => JSON dictionary of author dictionaries
    def get_all(self):
        authors = Author.query.all()
        json = jsonifyList(authors, "authors")
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # create new author => JSON dictionary with success or fail status
    def create(self, form):
        if form.validate == False:
            # return fail
            json = '{"operation":"create author", "status":"fail"}'
            return make_response(
                json,
                self.return_code_fail,
                self.headers)
            
        first_name = form.first_name.data
        surname = form.surname.data
        date_birth = form.date_birth.data
        date_death = form.date_death.data
        self.db.session.add(Author(first_name=first_name, surname=surname, date_birth=date_birth, date_death=date_death))
        self.db.session.commit()
        # return success
        json = '{"operation":"create author", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)
    
    # update existing author => JSON dictionary with success or fail status
    def update(self, form):
        if form.validate == False:
            # return fail
            json = '{"id":' + str(form.id.data) + ', "operation":"update author", "status":"fail"}'
            self.headers = {"Content-Type": "application/json"}
            return make_response(
                json,
                self.return_code_fail,
                self.headers)

        id = form.id.data
        first_name = form.first_name.data
        surname = form.surname.data
        date_birth = form.date_death.data
        date_death = form.date_death.data
        if id == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"update author", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        self.db.session.query(Author).filter(Author.id==id).\
            update({"first_name":first_name, "surname":surname, "date_birth":date_birth, "date_death":date_death})
        self.db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"update author", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # delete existing author => JSON dictionary with success or fail status
    def delete(self, id):
        if id == 0:
            # return fail
            json = '{"id":' + str(id) + ', "operation":"delete", "status":"fail"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        Author.query.filter(Author.id == id).delete()
        self.db.session.commit()
        # return success
        json = '{"id":' + str(id) + ', "operation":"delete", "status":"success"}'
        return make_response(
            json,
            self.return_code_success,
            self.headers)
    
    # get specified author => JSON author dictionary
    def get(self, id):
        authors = Author.query.filter(Author.id == id)
        if authors.count() == 0:
            # return not found
            json = '{"operation":"get", "status":"not found"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        # return success
        json = authors.first().jsonify()
        return make_response(
            json,
            self.return_code_success,
            self.headers)

    # find an author by first name or surname => JSON dictionary of author dictionaries
    def search(self, form):
        first_name = form.first_name.data
        if first_name != "":
            first_name = "{}%".format(first_name)
        surname = form.surname.data
        if surname != "":
            surname = "{}%".format(surname)
        if first_name == "" and surname == "":
            # return not found
            json = '{"operation":"get", "status":"not found"}'
            return make_response(
                json,
                self.return_code_not_found,
                self.headers)
        
        authors = Author.query.filter(or_(Author.first_name.ilike(first_name), Author.surname.ilike(surname)))
        json = jsonifyList(authors, "authors")
        return make_response(
            json,
            self.return_code_success,
            self.headers)
