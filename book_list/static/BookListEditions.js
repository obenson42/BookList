// classes
class Edition {
    constructor(id, isbn, datePublished, bookID, publisherID, bookTitle, publisherName) {
        this.id = id;
        this.isbn = isbn;
        this.datePublished = datePublished;
        this.bookID = bookID;
        this.publisherID = publisherID;
        this.bookTitle = bookTitle;
        this.publisherName = publisherName;
    }
}

class EditionList {
    constructor() {
        this.allEditions = [];
    }

    setContent(data) {
        this.allEditions = [];
        for (let x of data) {
            const edition = new Edition(x["id"], x["isbn"], x["date_published"], x["book_id"], x["publisher_id"], x["book_title"], x["publisher_name"]);
            this.allEditions.push(edition);
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
        const bookID = $("#book_id").val();
        const self = this;
        $.getJSON("/editions/?" + $.param({ "book_id": bookID }), function (data) {
            self.setContent(data["editions"]);
        })
            .fail(function () {
                alert("Problem getting edition list");
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

    addEdition() {
        const editionISBN = $("#edition_isbn").val();
        const editionDatePublished = $("#edition_date_published").val();
        const editionBookID = $("#edition_book_id").val();
        const editionPublisherID = $("#edition_publisher_id").val();
        const self = this;
        $.ajax({
            method: "PUSH",
            url: "/edition/",
            data: { id: 0, isbn: editionISBN, date_published: editionDatePublished, book_id: editionBookID, publisher_id: editionPublisherID },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see edition has been added
                self.viewAll();
            })
            .fail(function () {
                alert("Problem adding edition");
            });
    }

    updateEdition() {
        const editionID = $("#edition_id").val();
        const editionISBN = $("#edition_isbn").val();
        const editionDatePublished = $("#edition_date_published").val();
        const editionBookID = $("#edition_book_id").val();
        const editionPublisherID = $("#edition_publisher_id").val();
        const self = this;
        $.ajax({
            method: "PUT",
            url: "/edition/",
            data: { id: editionID, isbn: editionISBN, date_published: editionDatePublished, book_id: editionBookID, publisher_id: editionPublisherID },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see edition has been update
                self.viewAll();
            })
            .fail(function () {
                alert("Problem updating edition");
            });
    }

    deleteEdition() {
        const editionID = $("#edition_id").val();
        const self = this;
        $.ajax({
            method: "DELETE",
            url: "/edition/?" + $.param({ "id": editionID }),
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see edition has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem deleting edition");
            });
    }

    // form clearing/updating from user interaction
    clearForm() {
        // clear any previous highlighted row
        this.clearPrevHighlight();
        // clear the inputs
        $("#edition_id").val(0);
        $("#edition_isbn").val("");
        $("#edition_date_published").val("");
        //$("#edition_book_id").val(0);
        $("#edition_publisher_id").val(0);
        $("#edition_publisher").val("");
        // disable buttons dependent on a table row having been clicked
        $("#btn_add_edition").prop("disabled", true);
        $("#btn_update_edition").prop("disabled", true);
        $("#btn_delete_edition").prop("disabled", true);
    }

    clearPrevHighlight() {
        // clear previous row hightlight if there was one
        const prevID = $("#edition_id").val();
        if (prevID !== "0") {
            // un-highlight row
            $("#edition" + prevID + " td").each(function () {
                $(this).css({ backgroundColor: "" });
            });
        }
    }

    // called by inputs when text is entered, updates which buttons are disabled
    fieldsChanged() {
        const editionID = $("#edition_id").val();
        const editionISBN = $("#edition_isbn").val();
        const editionBookID = $("#edition_book_id").val();
        const editionPublisherID = $("#edition_publisher_id").val();
        $("#btn_add_edition").prop("disabled", (editionID !== "0" || editionISBN === ""));
        $("#btn_update_edition").prop("disabled", (editionID === "0"));
    }

    // get likely author name from db based on first few characters of surname
    // also update available buttons
    publisherLookup() {
        this.fieldsChanged();
        const editionPublisher = $("#edition_publisher").val();
        if (editionPublisher.length > 3) {
            const pos = editionPublisher.length;
            $.getJSON("/publisher_search/?" + $.param({ "name": editionPublisher }), function (data) {
                const x = data["publishers"][0];
                if (x) {
                    const publisher = new Publisher(x["id"], x["name"]);
                    $("#edition_publisher_id").val(x.id);
                    $("#edition_publisher").val(x.name);
                    $("#edition_publisher").caretTo(pos);
                }
            })
                .fail(function () {
                    alert("Problem in publisher lookup");
                });
        }
    }
    // JSON to HTML functions
    displayList() {
        let out = "";
        for (let i = 0; i < this.allEditions.length; i++) {
            const edition = this.allEditions[i];
            out += '<tr id="edition' + edition.id + '">';
            out += '<td>' + edition.isbn + '</td>';
            out += '<td>' + edition.datePublished + '</td>';
            out += '<td>' + edition.publisherName + '</td>';
            out += '</tr>';
        }
        $("#edition_list").find("tbody").empty();
        $("#edition_list").find("tbody").append(out);
        // disable buttons dependent on a table row having been clicked
        $("#btn_update_edition").prop("disabled", true);
        $("#btn_delete_edition").prop("disabled", true);
    }

    fillFieldsFromEdition(edition) {
        $("#edition_id").val(edition.id);
        $("#edition_isbn").val(edition.isbn);
        $("#edition_date_published").val(edition.datePublished);
        $("#edition_book_id").val(edition.bookID);
        $("#edition_publisher_id").val(edition.publisherID);
        $("#edition_publisher").val(edition.publisherName);
        // update which buttons are disabled
        $("#btn_add_edition").prop("disabled", true);
        $("#btn_update_edition").prop("disabled", true); // can't update until user changes something
        $("#btn_delete_edition").prop("disabled", false);
    }

    get numEditions() {
        return this.allEditions.length;
    }

    edition(i) {
        return this.allEditions[i];
    }

    editionByID(id) {
        return this.allEditions.find(obj => obj.id === id);
    }

    showEditionsByPublisher(publisherID) {
        this.clearPrevHighlight();
        this.clearForm();
        if (publisherID !== 0) {
            const self = this;
            $.getJSON("/editions_by_publisher/?" + $.param({ "publisher_id": publisherID }), function (data) {
                self.setContent(data["editions"]);
            })
                .fail(function () {
                    alert("Problem in loading editions by publisher");
                });
        }
    }
}

// create an instance of EditionList for all the UI to link to
gEditionList = new EditionList();

$(document).ready(function () {
    // add event to inputs
    $("#edition_isbn").on("input", function () {
        gEditionList.fieldsChanged();
    });
    $("#edition_publisher").on("input", function () {
        gEditionList.publisherLookup();
    });
    $("#edition_date_published").on("input", function () {
        gEditionList.fieldsChanged();
    });
    // add events to buttons
    $("#btn_view_all_editions").click(function () {
        gEditionList.viewAll(this);
    });
    $("#btn_add_edition").click(function () {
        gEditionList.addEdition();
    });
    $("#btn_update_edition").click(function () {
        gEditionList.updateEdition();
    });
    $("#btn_clear_form_edition").click(function () {
        gEditionList.clearForm();
    });
    $("#btn_delete_edition").click(function () {
        gEditionList.deleteEdition();
    });
    // add event to table rows
    $("#edition_list").delegate('tr', 'click', function () {
        gEditionList.clearPrevHighlight();
        // fill inputs with values for clicked row
        const id = parseInt($(this).attr("id").substring(7));
        for (let i = 0; i < gEditionList.numEditions; i++) {
            const edition = gEditionList.edition(i);
            if (edition['id'] === id) {
                gEditionList.fillFieldsFromEdition(edition);
                // highlight row clicked on so user can check they clicked the right one
                $("td", this).each(function () {
                    $(this).css({ backgroundColor: "#f8f9fa" });
                });
                break;
            }
        }
    });
});
