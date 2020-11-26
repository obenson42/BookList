// classes
class Book {
    constructor(id, title, authorFirstName, authorSurname, year, authorID) {
        this.id = id;
        this.title = title;
        this.authorFirstName = authorFirstName;
        this.authorSurname = authorSurname;
        this.year = year;
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
            const book = new Book(x["id"], x["title"], x["author_first_name"], x["author_surname"], x["year"], x["author_id"]);
            this.allBooks.push(book);
        }
        this.displayList();
        gLastUpdateBooks = Date.now();
    }

    // button methods
    viewAll(btn) {
        if(btn) {
            // disable button
            $(btn).prop("disabled", true);
            // add spinner to button
            $(btn).html(
                '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
            );
        }
        const self = this;
        $.getJSON("/books/", function (data) {
            self.setContent(data["books"]);
        })
            .fail(function () {
                alert("Problem getting book list");
            })
            .always(function () {
                if(btn) {
                    // remove spinner to button
                    $(btn).html(
                        'View All'
                    );
                    // enable button
                    $(btn).prop("disabled", false);
                }
            });
    }

    addBook() {
        const bookTitle = $("#book_title").val();
        const bookAuthorFirstName = $("#book_author_first_name").val();
        const bookAuthorSurname = $("#book_author_surname").val();
        const bookYear = $("#book_year").val();
        const self = this;
        $.ajax({
            method: "PUSH",
            url: "/book/",
            data: { id: 0, title: bookTitle, author_first_name: bookAuthorFirstName, author_surname: bookAuthorSurname, year: bookYear},
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
        const bookID = $("#book_id").val();
        const bookTitle = $("#book_title").val();
        const bookAuthorFirstName = $("#book_author_first_name").val();
        const bookAuthorSurname = $("#book_author_surname").val();
        const bookYear = $("#book_year").val();
        const self = this;
        $.ajax({
            method: "PUT",
            url: "/book/",
            data: { id: bookID, title: bookTitle, author_first_name: bookAuthorFirstName, author_surname: bookAuthorSurname, year: bookYear },
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

    deconsteBook() {
        const bookID = $("#book_id").val();
        const self = this;
        $.ajax({
            method: "DEconstE",
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
                alert("Problem deconsting book");
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
        const bookTitle = $("#book_title").val();
        const bookAuthorFirstName = $("#book_author_first_name").val();
        const bookAuthorSurname = $("#book_author_surname").val();
        const bookYear = $("#book_year").val();
        const self = this;
        $.getJSON("/books_search/?title=" + bookTitle + "&author_first_name=" + bookAuthorFirstName + "&author_surname=" + bookAuthorSurname + "&year=" + bookYear, function (data) {
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
        // disable buttons dependent on a table row having been clicked
        $("#btn_search").prop("disabled", true);
        $("#btn_add_book").prop("disabled", true);
        $("#btn_update_book").prop("disabled", true);
        $("#btn_deconste_book").prop("disabled", true);
        // disable link to author page
        $("#link_current_author").removeClass("text-primary");
        $("#link_current_author").addClass("text-muted");
    }

    clearPrevHighlight() {
        // clear previous row hightlight if there was one
        const prevID = $("#book_id").val();
        if (prevID !== "0") {
            // un-highlight row
            $("#book" + prevID + " td").each(function () {
                $(this).css({ backgroundColor: "" });
            });
        }
    }

    // called by inputs when text is entered, updates which buttons are disabled
    fieldsChanged() {
        const bookID = $("#book_id").val();
        const bookTitle = $("#book_title").val();
        const bookAuthorFirstName = $("#book_author_first_name").val();
        const bookAuthorSurname = $("#book_author_surname").val();
        const bookYear = $("#book_year").val();
        const bookAuthorID = $("#book_author_id").val();
        $("#btn_search").prop("disabled", (bookTitle === "" && bookAuthorFirstName === "" && bookAuthorSurname === "" && bookYear === ""));
        $("#btn_add_book").prop("disabled", (bookID !== "0" || bookTitle === "" || bookAuthorFirstName === "" || bookAuthorSurname === "" || bookYear === ""));
        $("#btn_update_book").prop("disabled", (bookID === "0"));
    }

    // get likely author name from db based on first few characters of first name
    // also update available buttons
    authorLookupFirstName() {
        this.fieldsChanged();
        const bookAuthorFirstName = $("#book_author_first_name").val();
        if (bookAuthorFirstName.length > 3) {
            const pos = bookAuthorFirstName.length;
            $.getJSON("/author_search/?" + $.param({ "first_name": bookAuthorFirstName, "surname": "" }), function (data) {
                const x = data["authors"][0];
                if (x) {
                    const author = new Author(x["id"], x["first_name"], x["surname"], x["date_birth"], x["date_death"]);
                    $("#book_author_id").val(x.id);
                    $("#book_author_first_name").val(x.first_name);
                    $("#book_author_surname").val(x.surname);
                    $("#book_author_firstname").caretTo(pos);
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
        const bookAuthorSurname = $("#book_author_surname").val();
        if (bookAuthorSurname.length > 3) {
            const pos = bookAuthorSurname.length;
            $.getJSON("/author_search/?" + $.param({ "first_name": "", "surname": bookAuthorSurname }), function (data) {
                const x = data["authors"][0];
                if (x) {
                    const author = new Author(x["id"], x["first_name"], x["surname"],  x["date_birth"], x["date_death"]);
                    $("#book_author_id").val(x.id);
                    $("#book_author_first_name").val(x.first_name);
                    $("#book_author_surname").val(x.surname);
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
            const book = this.allBooks[i];
            out += '<tr id="book' + book.id + '">';
            out += '<td>' + book.title + '</td>';
            out += '<td>' + book.authorFirstName + ' ' + book.authorSurname + '</td>';
            out += '<td>' + book.year + '</td>';
            out += '</tr>';
        }
        $("#book_list").find("tbody").empty();
        $("#book_list").find("tbody").append(out);
        // disable buttons dependent on a table row having been clicked
        $("#btn_update_book").prop("disabled", true);
        $("#btn_deconste_book").prop("disabled", true);
    }

    fillFieldsFromBook(book) {
        $("#book_id").val(book.id);
        $("#book_title").val(book.title);
        $("#book_author_first_name").val(book.authorFirstName);
        $("#book_author_surname").val(book.authorSurname);
        $("#book_year").val(book.year);
        // update which buttons are disabled
        $("#btn_add_book").prop("disabled", true);
        $("#btn_update_book").prop("disabled", true); // can't update until user changes something
        $("#btn_deconste_book").prop("disabled", false);
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
            const self = this;
            $.getJSON("/books_by_author/?" + $.param({ "author_id": authorID }), function (data) {
                self.setContent(data["books"]);
            })
                .fail(function () {
                    alert("Problem in loading books by author");
                });
        }
    }

    showBooksByPublisher(publisherID) {
        this.clearPrevHighlight();
        this.clearForm();
        if (publisherID !== 0) {
            const self = this;
            $.getJSON("/books_by_publisher/?" + $.param({ "publisher_id": publisherID }), function (data) {
                self.setContent(data["books"]);
            })
                .fail(function () {
                    alert("Problem in loading books by publisher");
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
    $("#btn_deconste_book").click(function () {
        gBookList.deconsteBook();
    });
    $("#link_current_author").click(function () {
        let bookID = $("#book_id").val();
        if (bookID !== "") {
            bookID = parseInt(bookID);
            const book = gBookList.bookByID(bookID);
            if (book !== undefined) {
                goPageAuthor(book.authorID)
            }
        }
    })
    // add event to table rows
    $("#book_list").delegate('tr', 'click', function () {
        gBookList.clearPrevHighlight();
        // fill inputs with values for clicked row
        const id = parseInt($(this).attr("id").substring(4));
        for (let i = 0; i < gBookList.numBooks; i++) {
            const book = gBookList.book(i);
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

function chechForUpdatesBooks() {
    $.getJSON("/last_update_books/", function (data) {
        clearInterval(gUpdateBooksInterval);
        if(data["last_update"] !== "None") {
            const lastDbUpdate = Date.parse(data["last_update"]);
            if(lastDbUpdate - gLastUpdateBooks > 10) {
                gBookList.viewAll();
            }
        }
        gUpdateBooksInterval = setInterval(chechForUpdatesBooks, 5000);
    })
    .fail(function () {
        alert("Problem in update check");
        clearInterval(gUpdateBooksInterval);
    });
}
var gLastUpdateBooks = Date.now();
var gUpdateBooksInterval = setInterval(chechForUpdatesBooks, 5000);