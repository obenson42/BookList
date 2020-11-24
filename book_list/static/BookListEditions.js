// classes
class Edition {
    constructor(id, isbn, pub_date, bookID, publisherID) {
        this.id = id;
        this.isbn = isbn;
        this.pub_date = pub_date;
        this.bookID = bookID;
        this.publisherID = publisherID;
    }
}

class EditionList {
    constructor() {
        this.allEditions = [];
    }

    setContent(data) {
        this.allEditions = [];
        for (let x of data) {
            let edition = new Edition(x["id"], x["isbn"], x["date_published"], x["book_id"], x["publisher_id"]);
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
        const self = this;
        $.getJSON("/editions/", function (data) {
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
        let self = this;
        $.ajax({
            method: "PUSH",
            url: "/edition/",
            data: { id: 0, isbn: editionISBN, date_published: editionDatePublished },
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
        const self = this;
        $.ajax({
            method: "PUT",
            url: "/edition/",
            data: { id: editionID, isbn: editionISBN, date_published: editionDatePublished },
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
        // disable buttons dependent on a table row having been clicked
        $("#btn_add_edition").prop("disabled", true);
        $("#btn_update_edition").prop("disabled", true);
        $("#btn_delete_edition").prop("disabled", true);
    }

    clearPrevHighlight() {
        // clear previous row hightlight if there was one
        let prevID = $("#edition_id").val();
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

    // JSON to HTML functions
    displayList() {
        let out = "";
        for (let i = 0; i < this.allEditions.length; i++) {
            const edition = this.allEditions[i];
            out += '<tr id="edition' + edition.id + '">';
            out += '<td>' + edition.isbn + '</td>';
            out += '<td>' + edition.date_published + '</td>';
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
        $("#edition_date_published").val(edition.date_published);
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
        let id = parseInt($(this).attr("id").substring(7));
        for (let i = 0; i < gEditionList.numEditions; i++) {
            let edition = gEditionList.edition(i);
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
