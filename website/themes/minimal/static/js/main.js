/**
 * Initializes all UI elements
 */
function init() {
    // Init the highlight.js library
    hljs.initHighlightingOnLoad();

    iwanttoreadmore.init();
}

if (document.readyState !== "loading") {
    init();
} else {
    document.addEventListener("DOMContentLoaded", init);
}
