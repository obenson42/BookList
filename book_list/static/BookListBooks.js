// classes
class Book {
    constructor(id, title, authorFirstName, authorSurname, year, isbn, authorID) {
        this.id = id;
        this.title = title;
        this.authorFirstName = authorFirstName;
        this.authorSurname = authorSurname;
        this.year = year;
        this.isbn = isbn;
        this.authorID = authorID;
    }
}

class BookList {
    constructor() {
        this.allBooks = [];
    }

    setContent(data) {
        this.allBooks = [];
        for (let x of data) {
            let book = new Book(x["id"], x["title"], x["author_first_name"], x["author_surname"], x["year"], x["isbn"], x["author_id"]);
            this.allBooks.push(book);
        }
        this.displayList();
    }

    // button methods
    viewAll(btn) {
        // disable button
        $(btn).prop("disabled", true);
        // add spinner to button
        $(btn).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
        );
        let self = this;
        $.getJSON("/books/", function (data) {
            self.setContent(data["books"]);
        })
            .fail(function () {
                alert("Problem getting book list");
            })
            .always(function () {
                // remove spinner to button
                $(btn).html(
                    'View All'
                );
                // enable button
                $(btn).prop("disabled", false);
            });
    }

    addBook() {
        let bookTitle = $("#book_title").val();
        let bookAuthorFirstName = $("#book_author_first_name").val();
        let bookAuthorSurname = $("#book_author_surname").val();
        let bookYear = $("#book_year").val();
        let bookISBN = $("#book_isbn").val().trim();
        let self = this;
        $.ajax({
            method: "PUSH",
            url: "/book/",
            data: { id: 0, title: bookTitle, author_first_name: bookAuthorFirstName, author_surname: bookAuthorSurname, year: bookYear, isbn: bookISBN },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see book has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem adding book");
            });
    }

    updateBook() {
        let bookID = $("#book_id").val();
        let bookTitle = $("#book_title").val();
        let bookAuthorFirstName = $("#book_author_first_name").val();
        let bookAuthorSurname = $("#book_author_surname").val();
        let bookYear = $("#book_year").val();
        let bookISBN = $("#book_isbn").val();
        let self = this;
        $.ajax({
            method: "PUT",
            url: "/book/",
            data: { id: bookID, title: bookTitle, author_first_name: bookAuthorFirstName, author_surname: bookAuthorSurname, year: bookYear, isbn: bookISBN },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see book has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem updating book");
            });
    }

    deleteBook() {
        let bookID = $("#book_id").val();
        let self = this;
        $.ajax({
            method: "DELETE",
            url: "/book/?" + $.param({ "id": bookID }),
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see book has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem deleting book");
            });
    }

    search(btn) {
        // disable button
        $(btn).prop("disabled", true);
        // add spinner to button
        $(btn).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
        );
        // get field values and send to search
        let bookTitle = $("#book_title").val();
        let bookAuthorFirstName = $("#book_author_first_name").val();
        let bookAuthorSurname = $("#book_author_surname").val();
        let bookYear = $("#book_year").val();
        let bookISBN = $("#book_isbn").val();
        let self = this;
        $.getJSON("/search/?title=" + bookTitle + "&author_first_name=" + bookAuthorFirstName + "&author_surname=" + bookAuthorSurname + "&year=" + bookYear + "&isbn=" + bookISBN, function (data) {
            self.setContent(data["books"]);
        })
            .fail(function () {
                alert("Problem searching book list");
            })
            .always(function () {
                // remove spinner to button
                $(btn).html(
                    'Search'
                );
                // enable button
                $(btn).prop("disabled", false);
            });
    }

    // form clearing/updating from user interaction
    clearForm() {
        // clear any previous highlighted row
        this.clearPrevHighlight();
        // clear the inputs
        $("#book_id").val(0);
        $("#book_title").val("");
        $("#book_author_first_name").val("");
        $("#book_author_surname").val("");
        $("#book_year").val("");
        $("#book_isbn").val("");
        // disable buttons dependent on a table row having been clicked
        $("#btn_search").prop("disabled", true);
        $("#btn_add_book").prop("disabled", true);
        $("#btn_update_book").prop("disabled", true);
        $("#btn_delete_book").prop("disabled", true);
        // disable link to author page
        $("#link_current_author").removeClass("text-primary");
        $("#link_current_author").addClass("text-muted");
    }

    clearPrevHighlight() {
        // clear previous row hightlight if there was one
        let prevID = $("#book_id").val();
        if (prevID !== "0") {
            // un-highlight row
            $("#book" + prevID + " td").each(function () {
                $(this).css({ backgroundColor: "" });
            });
        }
    }

    // called by inputs when text is entered, updates which buttons are disabled
    fieldsChanged() {
        let bookID = $("#book_id").val();
        let bookTitle = $("#book_title").val();
        let bookAuthorFirstName = $("#book_author_first_name").val();
        let bookAuthorSurname = $("#book_author_surname").val();
        let bookYear = $("#book_year").val();
        let bookISBN = $("#book_isbn").val();
        $("#btn_search").prop("disabled", (bookTitle === "" && bookAuthorFirstName === "" && bookAuthorSurname === "" && bookYear === "" && bookISBN === ""));
        $("#btn_add_book").prop("disabled", (bookID !== "0" || bookTitle === "" || bookAuthorFirstName === "" || bookAuthorSurname === "" || bookYear === "" || bookISBN === ""));
        $("#btn_update_book").prop("disabled", (bookID === "0"));
    }

    // get likely author name from db based on first few characters of first name
    // also update available buttons
    authorLookupFirstName() {
        this.fieldsChanged();
        let bookAuthorFirstName = $("#book_author_first_name").val();
        if (bookAuthorFirstName.length > 3) {
            let pos = bookAuthorFirstName.length;
            $.getJSON("/author_by_name/?" + $.param({ "first_name": bookAuthorFirstName, "surname": "" }), function (data) {
                if ((data !== "") && (data['first_name'] || data['surname'])) {
                    $("#book_author_first_name").val(data['first_name']);
                    $("#book_author_surname").val(data['surname']);
                    $("#book_author_first_name").caretTo(pos);
                }
            })
                .fail(function () {
                    alert("Problem in author lookup");
                });
        }
    }

    // get likely author name from db based on first few characters of surname
    // also update available buttons
    authorLookupSurname() {
        this.fieldsChanged();
        let bookAuthorSurname = $("#book_author_surname").val();
        if (bookAuthorSurname.length > 3) {
            let pos = bookAuthorSurname.length;
            $.getJSON("/author_by_name/?" + $.param({ "first_name": "", "surname": bookAuthorSurname }), function (data) {
                if ((data !== "") && (data['first_name'] || data['surname'])) {
                    $("#book_author_first_name").val(data['first_name']);
                    $("#book_author_surname").val(data['surname']);
                    $("#book_author_surname").caretTo(pos);
                }
            })
                .fail(function () {
                    alert("Problem in author lookup");
                });
        }
    }

    // JSON to HTML functions
    displayList() {
        let out = "";
        for (let i = 0; i < this.allBooks.length; i++) {
            let book = this.allBooks[i];
            out += '<tr id="book' + book.id + '"><td>' + book.title + '</td><td>' + book.authorFirstName + ' ' + book.authorSurname + '</td><td>' + book.year + '</td><td>' + book.isbn + '</td></tr>';
        }
        $("#book_list").find("tbody").empty();
        $("#book_list").find("tbody").append(out);
        // disable buttons dependent on a table row having been clicked
        $("#btn_update_book").prop("disabled", true);
        $("#btn_delete_book").prop("disabled", true);
    }

    fillFieldsFromBook(book) {
        $("#book_id").val(book.id);
        $("#book_title").val(book.title);
        $("#book_author_first_name").val(book.authorFirstName);
        $("#book_author_surname").val(book.authorSurname);
        $("#book_year").val(book.year);
        $("#book_isbn").val(book.isbn);
        // update which buttons are disabled
        $("#btn_add_book").prop("disabled", true);
        $("#btn_update_book").prop("disabled", true); // can't update until user changes something
        $("#btn_delete_book").prop("disabled", false);
        // enable link to author page
        $("#link_current_author").removeClass("text-muted");
        $("#link_current_author").addClass("text-primary");
    }

    get numBooks() {
        return this.allBooks.length;
    }

    book(i) {
        return this.allBooks[i];
    }

    bookByID(id) {
        return this.allBooks.find(obj => obj.id === id);
    }

    showBooksByAuthor(authorID) {
        this.clearPrevHighlight();
        this.clearForm();
        if (authorID !== 0) {
            let self = this;
            $.getJSON("/books_by_author/?" + $.param({ "author_id": authorID }), function (data) {
                self.setContent(data["books"]);
            })
                .fail(function () {
                    alert("Problem in loading books by author");
                });
        }
    }
}

// create an instance of BookList for all the UI to link to
gBookList = new BookList();

$(document).ready(function () {
    // add event to inputs
    $("#book_title").on("input", function () {
        gBookList.fieldsChanged();
    });
    $("#book_author_first_name").on("input", function () {
        gBookList.authorLookupFirstName();
    });
    $("#book_author_surname").on("input", function () {
        gBookList.authorLookupSurname();
    });
    $("#book_year").on("input", function () {
        gBookList.fieldsChanged();
    });
    $("#book_isbn").on("input", function () {
        gBookList.fieldsChanged();
    });
    // add events to buttons
    $("#btn_view_all_books").click(function () {
        gBookList.viewAll(this);
    });
    $("#btn_search").click(function () {
        gBookList.search(this);
    });
    $("#btn_add_book").click(function () {
        gBookList.addBook();
    });
    $("#btn_update_book").click(function () {
        gBookList.updateBook();
    });
    $("#btn_clear_form_book").click(function () {
        gBookList.clearForm();
    });
    $("#btn_delete_book").click(function () {
        gBookList.deleteBook();
    });
    $("#link_current_author").click(function () {
        let bookID = $("#book_id").val();
        if (bookID !== "") {
            bookID = parseInt(bookID);
            let book = gBookList.bookByID(bookID);
            if (book !== undefined) {
                goPageAuthor(book.authorID)
            }
        }
    })
    // add event to table rows
    $("#book_list").delegate('tr', 'click', function () {
        gBookList.clearPrevHighlight();
        // fill inputs with values for clicked row
        let id = parseInt($(this).attr("id").substring(4));
        for (let i = 0; i < gBookList.numBooks; i++) {
            let book = gBookList.book(i);
            if (book['id'] === id) {
                gBookList.fillFieldsFromBook(book);
                // highlight row clicked on so user can check they clicked the right one
                $("td", this).each(function () {
                    $(this).css({ backgroundColor: "#f8f9fa" });
                });
                break;
            }
        }
    });
});
