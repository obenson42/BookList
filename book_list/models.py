from sqlalchemy import create_engine, Column, Integer, String, Sequence, Text, Date,PrimaryKeyConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
import datetime
import html
from book_list import db

class Author(db.Model):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    first_name = Column(Text(), nullable=False)
    surname = Column(Text(), nullable=False)
    date_birth = Column(Date, nullable=True)
    date_death = Column(Date, nullable=True)
    books = relationship('Book', backref=backref('author', lazy=True))

    def jsonify(self):
        json = '{"id":' + str(self.id)
        json += ',"first_name":"' + html.escape(self.first_name) + '"'
        json += ',"surname":"' + html.escape(self.surname) + '"'
        json += ',"date_birth":"' + (str(self.date_birth) if isinstance(self.date_birth, datetime.date) else "") + '"'
        json += ',"date_death":"' + (str(self.date_death) if isinstance(self.date_death, datetime.date) else "") + '"'
        json += '}'
        return json

    def __repr__(self):
        return '<Author: {}>'.format(self.surname)

class Book(db.Model):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(Text(), nullable=False)
    year = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    editions = relationship('Edition', backref=backref('book', lazy=True))

    def jsonify(self):
        json = '{"id":' + str(self.id)
        json += ',"title":"' + html.escape(self.title) + '"'
        json += ',"year":' + str(self.year)
        json += ',"author_id":' + (str(self.author_id) if isinstance(self.author_id, int) else "0")
        if self.author != None:
            json += ',"author_first_name":"' + self.author.first_name + '"'
            json += ',"author_surname":"' + self.author.surname + '"'
        json += '}'
        return json

    def __repr__(self):
        return '<Book: {}>'.format(self.title)
        
class Publisher(db.Model):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    name = Column(Text())
    editions = relationship('Edition', backref=backref('publisher', lazy=True))

    def jsonify(self):
        json = '{"id":' + str(self.id)
        json += ',"name":"' + html.escape(self.name) + '"'
        json += '}'
        return json

    def __repr__(self):
        return '<Publisher: {}>'.format(self.name)

class Edition(db.Model):
    __tablename__ = 'edition'
    id = Column(Integer, primary_key=True)
    date_pub = Column(Date)
    isbn = Column(Text())
    book_id = Column(Integer, ForeignKey('book.id'))
    publisher_id = Column(Integer, ForeignKey('publisher.id'))

    def jsonify(self):
        json = '{"id":' + str(self.id)
        json += ',"date_published":"' + (str(self.date_pub) if isinstance(self.date_pub, datetime.date) else "") + '"'
        json += ',"isbn":"' + html.escape(self.isbn) + '"'
        json += ',"book_id":' + (str(self.book_id) if isinstance(self.book_id, int) else "0")
        json += ',"publisher_id":' + (str(self.publisher_id) if isinstance(self.publisher_id, int) else "0")
        if self.book != None:
            json += ',"book_title":"' + self.book.title + '"'
        if self.publisher != None:
            json += ',"publisher_name":"' + self.publisher.name + '"'
        json += '}'
        return json

    def __repr__(self):
        return '<Edition: {}>'.format(self.isbn)
