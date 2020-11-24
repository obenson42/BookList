function goPageBook(authorID) {
    $("#page_books").show("slow");
    $("#page_authors").hide("slow");
    $("#page_publishers").hide("slow");
    $("#link_books, #link_authors").toggleClass("active");
    if(authorID !== undefined)
        gBookList.showBooksByAuthor(authorID);
}

function goPageAuthor(authorID) {
    $("#page_books").hide("slow");
    $("#page_authors").show("slow");
    $("#page_publishers").hide("slow");
    $("#link_books, #link_authors").toggleClass("active");
    if (authorID !== undefined)
        gAuthorList.showAuthor(authorID);
}

function goPagePublisher(bookID, authorID) {
    $("#page_books").hide("slow");
    $("#page_authors").hide("slow");
    $("#page_publishers").show("slow");
    if(bookID !== undefined)
        gPublisherList.showPublishersByBook(bookID);
    else if(authorID !== undefined)
        gPublisherList.showPublishersByAuthor(authorID);
}

$(document).ready(function () {
    // add event to inputs
    $("#link_books").click(function (event) {
        event.preventDefault();
        goPageBook();
    });
    $("#link_authors").click(function (event) {
        event.preventDefault();
        goPageAuthor();
    });
    $("#link_publishers").click(function (event) {
        event.preventDefault();
        goPagePublisher();
    });
});