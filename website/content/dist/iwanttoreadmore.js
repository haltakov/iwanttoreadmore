const iwanttoreadmore = {
    init: () => {
        // Inject the toast
        document.body.insertAdjacentHTML(
            "beforeend",
            '<div id="iwanttoreadmore-vote-toast"><h3>I Want To Read More</h3><p>Thank you! I will write more on this topic in the future!</p><small>Powered by <a href="https://iwanttoreadmore.com" target="_blank" rel="noopener">iwanttoreadmore.com</a></small></div>'
        );

        // Process all vote links
        document.querySelectorAll("[data-vote]").forEach((voteLink) => {
            // Add icon and set style
            voteLink.classList.add("iwanttoreadmore-vote-link");
            voteLink.innerHTML =
                '<svg viewBox="0 0 22 27"><circle r="5" cx="11" cy="5"/><rect ry="1.5" x="3" y="9" height="18" width="16" style="stroke:#fff;stroke-width:1.5"/><ellipse rx="3" ry="4" cx="3" cy="18.5" style="stroke:#fff;stroke-width:2"/><ellipse rx="3" ry="4" cx="19" cy="18.5" style="stroke:#fff;stroke-width:2"/></svg>';
            voteLink.setAttribute("title", "Click if you want me to write more about this topic in the future.");
            voteLink.setAttribute("aria-label", "Click if you want me to write more about this topic in the future.");

            // Add onclick event
            voteLink.onclick = (event) => {
                // Post the vote to the backend
                const url = `https://iwanttoreadmore.com/vote/${voteLink.getAttribute("data-vote")}`;
                fetch(url, { method: "post" });

                // Remove the link from the vote icon
                voteLink.removeAttribute("href");
                voteLink.onclick = null;
                voteLink.removeAttribute("data-vote");
                voteLink.style.color = "inherit";

                // Display the toast
                const toast = document.getElementById("iwanttoreadmore-vote-toast");
                toast.style.display = "block";
                setInterval(function () {
                    toast.style.display = "none";
                }, 10000);

                return false;
            };
        });
    },
};
