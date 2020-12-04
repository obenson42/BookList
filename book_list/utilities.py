from sqlalchemy import or_

from book_list import db, cache

from book_list.models import Author, Book, Publisher, Edition

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
