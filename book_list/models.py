from book_list import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Book: {}>'.format(self.title)
        
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text(), nullable=False)
    surname = db.Column(db.Text(), nullable=False)
    date_birth = db.Column(db.Date, nullable=True)
    date_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return '<Author: {}>'.format(self.surname)
