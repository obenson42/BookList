// classes
class Author {
    constructor(id, firstName, surname, date_birth, date_death) {
        this.id = id;
        this.firstName = firstName;
        this.surname = surname;
        this.date_birth = date_birth;
        this.date_death = date_death;
    }
}

class AuthorList {
    constructor() {
        this.allAuthors = [];
    }

    setContent(data) {
        this.allAuthors = [];
        for (let x of data) {
            const author = new Author(x["id"], x["first_name"], x["surname"], x["date_birth"], x["date_death"]);
            this.allAuthors.push(author);
        }
        this.displayList();
    }

    // button methods
    view_all(btn) {
        // disable button
        $(btn).prop("disabled", true);
        // add spinner to button
        $(btn).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
        );
        let self = this;
        $.getJSON("/authors/", function (data) {
            self.setContent(data["authors"]);
        })
            .fail(function () {
                alert("Problem getting author list");
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

    addAuthor() {
        const authorFirstName = $("#author_first_name").val();
        const authorSurname = $("#author_surname").val();
        const authorPhotoUrl = $("#author_photo_url").val();
        const authorDateBirth = $("#author_date_birth").val();
        const authorDateDeath = $("#author_date_death").val();
        const self = this;
        $.ajax({
            method: "PUSH",
            url: "/author/",
            data: { id: 0, first_name: authorFirstName, surname: authorSurname, photo_url: authorPhotoUrl, date_birth: authorDateBirth, date_death: authorDateDeath },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see author has been added
                self.view_all();
            })
            .fail(function () {
                alert("Problem adding author");
            });
    }

    updateAuthor() {
        const authorID = $("#author_id").val();
        const authorFirstName = $("#author_first_name").val();
        const authorSurname = $("#author_surname").val();
        const authorPhotoUrl = $("#author_photo_url").val();
        const authorDateBirth = $("#author_date_birth").val();
        const authorDateDeath = $("#author_date_death").val();
        const self = this;
        $.ajax({
            method: "PUT",
            url: "/author/",
            data: { id: authorID, first_name: authorFirstName, surname: authorSurname, photo_url: authorPhotoUrl, date_birth: authorDateBirth, date_death: authorDateDeath },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see author has been updated
                self.view_all();
            })
            .fail(function () {
                alert("Problem updating author");
            });
    }

    deleteAuthor() {
        let authorID = $("#author_id").val();
        let self = this;
        $.ajax({
            method: "DELETE",
            url: "/author/?" + $.param({ "id": authorID }),
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see author has gone
                self.view_all();
            })
            .fail(function () {
                alert("Problem deleting author");
            });
    }

    // form clearing/updating from user interaction
    clearForm() {
        // clear any previous highlighted row
        this.clearPrevHighlight();
        // clear the inputs
        $("#author_id").val(0);
        $("#author_first_name").val("");
        $("#author_surname").val("");
        $("#author_photo_url").val("");
        $("#author_date_birth").val("");
        $("#author_date_death").val("");
        // disable buttons dependent on a table row having been clicked
        $("#btn_add_author").prop("disabled", true);
        $("#btn_update_author").prop("disabled", true);
        $("#btn_delete_author").prop("disabled", true);
    }

    clearPrevHighlight() {
        // clear previous row hightlight if there was one
        let prevID = $("#author_id").val();
        if (prevID !== "0") {
            // un-highlight row
            $("#author" + prevID + " td").each(function () {
                $(this).css({ backgroundColor: "" });
            });
        }
    }

    // called by inputs when text is entered, updates which buttons are disabled
    fieldsChanged() {
        const authorID = $("#author_id").val();
        const authorFirstName = $("#author_first_name").val();
        const authorSurname = $("#author_surname").val();
        const authorPhotoUrl = $("#author_photo_url").val();
        const authorDateBirth = $("#author_date_birth").val();
        const authorDateDeath = $("#author_date_death").val();
        $("#btn_add_author").prop("disabled", (authorID !== "0" || authorFirstName === "" || authorSurname === ""));
        $("#btn_update_author").prop("disabled", (authorID === "0"));
        $("#btn_show_books").prop("disabled", (authorID === "0"));
    }

    // get likely author name from db based on first few characters of first name
    // also update available buttons
    authorLookupFirstName() {
        this.fieldsChanged();
        if ($("#author_id").val() !== "0") return;

        let authorFirstName = $("#author_first_name").val();
        if (authorFirstName.length > 3) {
            let pos = authorFirstName.length;
            $.getJSON("/author_search/?" + $.param({ "first_name": authorFirstName, "surname": "" }), function (data) {
                const x = data["authors"][0];
                if (x) {
                    const author = new Author(x["id"], x["first_name"], x["surname"], x["date_birth"], x["date_death"]);
                    $("#author_id").val(x.id);
                    $("#author_first_name").val(x.first_name);
                    $("#author_surname").val(x.surname);
                    $("#author_date_birth").val(x.date_birth);
                    $("#author_date_death").val(x.date_death);
                    $("#author_firstname").caretTo(pos);
                }
            })
                .fail(function () {
                    alert("Problem in author lookup by first name");
                });
        }
    }

    // get likely author name from db based on first few characters of surname
    // also update available buttons
    authorLookupSurname() {
        this.fieldsChanged();
        if ($("#author_id").val() !== "0") return;

        let authorSurname = $("#author_surname").val();
        if (authorSurname.length > 3) {
            let pos = authorSurname.length;
            $.getJSON("/author_search/?" + $.param({ "first_name": "", "surname": authorSurname }), function (data) {
                const x = data["authors"][0];
                if (x) {
                    const author = new Author(x["id"], x["first_name"], x["surname"], x["date_birth"], x["date_death"]);
                    $("#author_id").val(x.id);
                    $("#author_first_name").val(x.first_name);
                    $("#author_surname").val(x.surname);
                    $("#author_date_birth").val(x.date_birth);
                    $("#author_date_death").val(x.date_death);
                    $("#author_firstname").caretTo(pos);
                }
            })
                .fail(function () {
                    alert("Problem in author lookup by surname");
                });
        }
    }

    // JSON to HTML functions
    displayList() {
        let out = "";
        for (let i = 0; i < this.allAuthors.length; i++) {
            let author = this.allAuthors[i];
            out += '<tr id="author' + author.id + '"><td>' + author.surname + '</td><td>' + author.firstName + '</td></tr>';
        }
        $("#author_list").find("tbody").empty();
        $("#author_list").find("tbody").append(out);
        // disable buttons dependent on a table row having been clicked
        $("#btn_update_author").prop("disabled", true);
        $("#btn_delete_author").prop("disabled", true);
    }

    fillFieldsFromAuthor(author) {
        if (author === undefined)
            return;
        
        $("#author_id").val(author.id);
        $("#author_first_name").val(author.firstName);
        $("#author_surname").val(author.surname);
        $("#author_photo_url").val(author.photo_url);
        $("#author_date_birth").val(author.date_birth);
        $("#author_date_death").val(author.date_death);
        if (author.photo_url !== undefined && author.photo_url !== "") {
            //$("author_photo").add("<img src='" + author.photo_url + "' />")
        }
        // update which buttons are disabled
        $("#btn_add_author").prop("disabled", true);
        $("#btn_update_author").prop("disabled", true); // can't update until user changes something
        $("#btn_delete_author").prop("disabled", false);
        $("#btn_show_books").prop("disabled", false);
    }

    get numAuthors() {
        return this.allAuthors.length;
    }

    author(i) {
        return this.allAuthors[i];
    }

    authorByID(id) {
        let author = this.allAuthors.find(obj => obj.id === id);
        if (author === undefined) {
            // try to load from db
            let self = this;
            this.getAuthorFromDbByID(id).then(function (data) {
                if (data !== undefined) {
                    author = new Author(data['id'], data['first_name'], data['surname'], data['date_birth'], data['date_death']);
                    self.allAuthors.push(author);
                    self.displayList();
                    self.showAuthor(id);
                }
            });
        }
        return author;
    }

    // internal only
    getAuthorFromDbByID(id) {
        if (id !== undefined) {
            return $.getJSON("/author/?" + $.param({ "id": id }))
                .fail(function () {
                    alert("Problem in author lookup by id=" + id);
                });
        } else {
            return undefined;
        }
    }

    showAuthor(id) {
        this.clearForm();
        if (id != undefined) {
            let author = this.authorByID(id);
            if (author !== undefined) {
                this.fillFieldsFromAuthor(author);
                // highlight row clicked on so user can check they clicked the right one
                let row = $("#author" + id);
                $("td", row).each(function () {
                    $(row).css({ backgroundColor: "#f8f9fa" });
                });
            }
        }
    }
}

// create an instance of AuthorList for all the UI to link to
gAuthorList = new AuthorList();

$(document).ready(function () {
    // add event to inputs
    $("#author_first_name").on("input", function () {
        gAuthorList.authorLookupFirstName();
    });
    $("#author_surname").on("input", function () {
        gAuthorList.authorLookupSurname();
    });
    $("#author_photo_url").on("input", function () {
        gAuthorList.fieldsChanged();
    });
    $("#author_date_birth").on("input", function () {
        gAuthorList.fieldsChanged();
    });
    $("#author_date_death").on("input", function () {
        gAuthorList.fieldsChanged();
    });
    // add events to buttons
    $("#btn_view_all_authors").click(function () {
        gAuthorList.view_all(this);
    });
    $("#btn_show_books").click(function () {
        let authorID = $("#author_id").val();
        if (authorID !== "") {
            authorID = parseInt(authorID);
            goPageBook(authorID)
        }
    });
    $("#btn_add_author").click(function () {
        gAuthorList.addAuthor();
    });
    $("#btn_update_author").click(function () {
        gAuthorList.updateAuthor();
    });
    $("#btn_clear_form_author").click(function () {
        gAuthorList.clearForm();
    });
    $("#btn_delete_author").click(function () {
        gAuthorList.deleteAuthor();
    });
    // add event to table rows
    $("#author_list").delegate('tr', 'click', function () {
        gAuthorList.clearPrevHighlight();
        // fill inputs with values for clicked row
        let id = parseInt($(this).attr("id").substring(6));
        for (let i = 0; i < gAuthorList.numAuthors; i++) {
            let author = gAuthorList.author(i);
            if (author.id === id) {
                gAuthorList.fillFieldsFromAuthor(author);
                // highlight row clicked on so user can check they clicked the right one
                $("td", this).each(function () {
                    $(this).css({ backgroundColor: "#f8f9fa" });
                });
                break;
            }
        }
    });
});
