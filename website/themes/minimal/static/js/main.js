/**
 * Initializes all UI elements
 */
function init() {
    // Choose which navbar to show
    chooseNavbar();

    // Init the highlight.js library
    hljs.initHighlightingOnLoad();

    // Init the I Want To Read More script
    iwanttoreadmore.init();
}

/**
 * Chooses which navbar to show depending on if the user is loggen in or not
 */
function chooseNavbar() {
    if (document.cookie.includes("loggedin")) {
        document.getElementById("logged-out-nav").classList.add("hidden");
        document.getElementById("logged-in-nav").classList.remove("hidden");
    }
}

if (document.readyState !== "loading") {
    init();
} else {
    document.addEventListener("DOMContentLoaded", init);
}
