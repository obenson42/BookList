function goPageBook(authorID, publisherID) {
    $("#page_books").show("slow");
    $("#page_editions").hide("slow");
    $("#page_authors").hide("slow");
    $("#page_publishers").hide("slow");
    $("#link_authors, #link_publishers").removeClass("active");
    $("#link_books").addClass("active");
    if(authorID)
        gBookList.showBooksByAuthor(authorID);
    if(publisherID)
        gBookList.showBooksByPublisher(publisherID);
}

function goPageAuthor(authorID) {
    $("#page_books").hide("slow");
    $("#page_editions").hide("slow");
    $("#page_authors").show("slow");
    $("#page_publishers").hide("slow");
    $("#link_books, #link_publishers").removeClass("active");
    $("#link_authors").addClass("active");
    if (authorID !== undefined)
        gAuthorList.showAuthor(authorID);
}

function goPagePublisher(bookID, authorID) {
    $("#page_books").hide("slow");
    $("#page_editions").hide("slow");
    $("#page_authors").hide("slow");
    $("#page_publishers").show("slow");
    $("#link_books, #link_authors").removeClass("active");
    $("#link_publishers").addClass("active");
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

function sanitize(string) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        "/": '&#x2F;',
    };
    const reg = /[&<>"'/]/ig;
    return string.replace(reg, (match)=>(map[match]));
}