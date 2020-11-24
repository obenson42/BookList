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

#f 'DATABASE_URL' in os.environ:
#    db = Database(os.environ['DATABASE_URL'], 'require')
#else:
#    db = Database("dbname='store' user='postgres' password='postgres123' host='localhost' port='5433'", 'allow')
