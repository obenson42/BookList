// classes
class Publisher {
    constructor(id, name) {
        this.id = id;
        this.name = name;
    }
}

class PublisherList {
    constructor() {
        this.allPublishers = [];
    }

    setContent(data) {
        this.allPublishers = [];
        for (let x of data) {
            const publisher = new Publisher(x["id"], x["name"]);
            this.allPublishers.push(publisher);
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
        $.getJSON("/publishers/", function (data) {
            self.setContent(data["publishers"]);
        })
            .fail(function () {
                alert("Problem getting publisher list");
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

    addPublisher() {
        const publisherName = $("#publisher_name").val();
        const self = this;
        $.ajax({
            method: "PUSH",
            url: "/publisher/",
            data: { id: 0, name: publisherName },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see publisher has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem adding publisher");
            });
    }

    updatePublisher() {
        const publisherID = $("#publisher_id").val();
        const publisherName = $("#publisher_name").val();
        const self = this;
        $.ajax({
            method: "PUT",
            url: "/publisher/",
            data: { id: publisherID, name: publisherName },
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see publisher has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem updating publisher");
            });
    }

    deletePublisher() {
        const publisherID = $("#publisher_id").val();
        const self = this;
        $.ajax({
            method: "DELETE",
            url: "/publisher/?" + $.param({ "id": publisherID }),
            dataType: "json"
        })
            .done(function (result) {
                // clear the inputs
                self.clearForm();
                // get the list again so user can see publisher has gone
                self.viewAll();
            })
            .fail(function () {
                alert("Problem deleting publisher");
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
        const publisherName = $("#publisher_name").val();
        const self = this;
        $.getJSON("/publishers_search/?name=" + publisherName, function (data) {
            self.setContent(data["publishers"]);
        })
            .fail(function () {
                alert("Problem searching publisher list");
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
        $("#publisher_id").val(0);
        $("#publisher_name").val("");
        // disable buttons dependent on a table row having been clicked
        $("#btn_search").prop("disabled", true);
        $("#btn_add_publisher").prop("disabled", true);
        $("#btn_update_publisher").prop("disabled", true);
        $("#btn_delete_publisher").prop("disabled", true);
    }

    clearPrevHighlight() {
        // clear previous row hightlight if there was one
        const prevID = $("#publisher_id").val();
        if (prevID !== "0") {
            // un-highlight row
            $("#publisher" + prevID + " td").each(function () {
                $(this).css({ backgroundColor: "" });
            });
        }
    }

    // called by inputs when text is entered, updates which buttons are disabled
    fieldsChanged() {
        const publisherID = $("#publisher_id").val();
        const publisherName = $("#publisher_name").val();
        $("#btn_show_publisher_books").prop("disabled", (publisherID === "0"));
        $("#btn_add_publisher").prop("disabled", (publisherID !== "0" || publisherName === ""));
        $("#btn_update_publisher").prop("disabled", (publisherID === "0"));
    }

    // JSON to HTML functions
    displayList() {
        let out = "";
        for (let i = 0; i < this.allPublishers.length; i++) {
            const publisher = this.allPublishers[i];
            out += '<tr id="publisher' + publisher.id + '">';
            out += '<td>' + publisher.name + '</td>';
            out += '</tr>';
        }
        $("#publisher_list").find("tbody").empty();
        $("#publisher_list").find("tbody").append(out);
        // disable buttons dependent on a table row having been clicked
        $("#btn_update_publisher").prop("disabled", true);
        $("#btn_delete_publisher").prop("disabled", true);
    }

    fillFieldsFromPublisher(publisher) {
        $("#publisher_id").val(publisher.id);
        $("#publisher_name").val(publisher.name);
        // update which buttons are disabled
        $("#btn_add_publisher").prop("disabled", true);
        $("#btn_show_publisher_books").prop("disabled", false);
        $("#btn_update_publisher").prop("disabled", true); // can't update until user changes something
        $("#btn_delete_publisher").prop("disabled", false);
    }

    get numPublishers() {
        return this.allPublishers.length;
    }

    publisher(i) {
        return this.allPublishers[i];
    }

    publisherByID(id) {
        return this.allPublishers.find(obj => obj.id === id);
    }
//TODO
    showPublishersByAuthor(authorID) {
        this.clearPrevHighlight();
        this.clearForm();
        if (authorID !== 0) {
            const self = this;
            $.getJSON("/publishers_by_author/?" + $.param({ "author_id": authorID }), function (data) {
                self.setContent(data["publishers"]);
            })
                .fail(function () {
                    alert("Problem in loading publishers by author");
                });
        }
    }
}

// create an instance of PublisherList for all the UI to link to
gPublisherList = new PublisherList();

$(document).ready(function () {
    // add event to inputs
    $("#publisher_name").on("input", function () {
        gPublisherList.fieldsChanged();
    });
    // add events to buttons
    $("#btn_view_all_publishers").click(function () {
        gPublisherList.viewAll(this);
    });
    $("#btn_show_publisher_books").click(function () {
        const publisherID = $("#publisher_id").val();
        if (publisherID !== "") {
            goPageBook(null, parseInt(publisherID))
        }
    });
    $("#btn_add_publisher").click(function () {
        gPublisherList.addPublisher();
    });
    $("#btn_update_publisher").click(function () {
        gPublisherList.updatePublisher();
    });
    $("#btn_clear_form_publisher").click(function () {
        gPublisherList.clearForm();
    });
    $("#btn_delete_publisher").click(function () {
        gPublisherList.deletePublisher();
    });
    // add event to table rows
    $("#publisher_list").delegate('tr', 'click', function () {
        gPublisherList.clearPrevHighlight();
        // fill inputs with values for clicked row
        const id = parseInt($(this).attr("id").substring(9));
        for (let i = 0; i < gPublisherList.numPublishers; i++) {
            const publisher = gPublisherList.publisher(i);
            if (publisher['id'] === id) {
                gPublisherList.fillFieldsFromPublisher(publisher);
                // highlight row clicked on so user can check they clicked the right one
                $("td", this).each(function () {
                    $(this).css({ backgroundColor: "#f8f9fa" });
                });
                break;
            }
        }
    });
});
