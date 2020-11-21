function goPageBook(authorID) {
    $("#page_books").show("slow");
    $("#page_authors").hide("slow");
    $("#link_books, #link_authors").toggleClass("active");
    if(authorID !== undefined)
        gBookList.showBooksByAuthor(authorID);
}

function goPageAuthor(authorID) {
    $("#page_books").hide("slow");
    $("#page_authors").show("slow");
    $("#link_books, #link_authors").toggleClass("active");
    if (authorID !== undefined)
        gAuthorList.showAuthor(authorID);
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
});