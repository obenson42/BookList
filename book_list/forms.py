from wtforms import Form, DateField, IntegerField, StringField, validators

class BookForm(Form):
    id = IntegerField('book_id')
    title = StringField('book_title', [validators.Length(min=1, max=255)])
    author_first_name = StringField('book_author_first_name', [validators.Length(min=1, max=35)])
    author_surname = StringField('book_author_surname', [validators.Length(min=1, max=35)])
    year = IntegerField('book_year')
    author_id = IntegerField('book_author_id')

class AuthorForm(Form):
    id = IntegerField('author_id')
    first_name = StringField('author_first_name', [validators.Length(min=1, max=35)])
    surname = StringField('author_surname', [validators.Length(min=1, max=35)])
    date_birth = DateField('author_date_birth')
    date_death = DateField('author_date_death')

class PublisherForm(Form):
    id = IntegerField('publisher_id')
    name = StringField('publisher_name', [validators.Length(min=1, max=255)])

class EditionForm(Form):
    id = IntegerField('edition_id')
    isbn = StringField('edition_isbn', [validators.Length(min=10, max=13)])
    date_published = DateField('edition_date_published', [validators.DataRequired()])
    book_id = IntegerField('edition_book_id')
    publisher_id = IntegerField('edition_publisher_id')
