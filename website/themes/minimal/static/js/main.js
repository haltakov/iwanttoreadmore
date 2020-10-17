/**
 * Initializes all UI elements
 */
function init() {
    // Init the highlight.js library
    hljs.initHighlightingOnLoad();

    // Click events for all vote links
    Array.from(document.querySelectorAll("[data-vote]")).forEach(
        (e) =>
            (e.onclick = (event) => {
                // Post the vote to the backend
                const url = `https://iwanttoreadmore.com/vote/${e.getAttribute("data-vote")}`;
                fetch(url, { method: "post" });

                // Remove the link from the vote icon
                e.removeAttribute("href");
                e.onclick = null;
                e.removeAttribute("data-vote");
                e.style = "color: #4a5568;";

                // Display the toast
                const toast = document.getElementById("vote-toast");
                toast.classList.remove("hidden");
                setInterval(function () {
                    toast.classList.add("hidden");
                }, 10000);

                return false;
            })
    );
}

if (document.readyState !== "loading") {
    init();
} else {
    document.addEventListener("DOMContentLoaded", init);
}
