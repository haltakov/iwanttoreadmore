const iwanttoreadmore = {
    /**
     * Initialize the I Want To Read More script
     * @param config - optional configuration dictionary
     *
     * The following options are supported:
     * - voteLink: content of the vote link (by default the I Want To Read More icon). HTML can be used. Set to empty to use the original content of the link.
     * - tooltip: text to show in the tooltip. Set to empty to hide the tooltip.
     * - messageTitle: title of the message shown after voting
     * - messageText: text of the message shown after voting
     * - messageDuration: duration that the message will be shown after voting in seconds. Set to 0 to disable.
     */
    init: (config = {}) => {
        // Check if the page contains voting links and abort if not
        if (document.querySelectorAll("[data-vote]").length == 0) return;

        // Process the configuration and setup defaults
        const configVoteLink =
            "voteLink" in config
                ? config.voteLink
                : '<svg viewBox="0 0 22 27"><circle r="5" cx="11" cy="5"/><rect ry="1.5" x="3" y="9" height="18" width="16" style="stroke:#fff;stroke-width:1.5"/><ellipse rx="3" ry="4" cx="3" cy="18.5" style="stroke:#fff;stroke-width:2"/><ellipse rx="3" ry="4" cx="19" cy="18.5" style="stroke:#fff;stroke-width:2"/></svg>';
        const configTooltip =
            "tooltip" in config ? config.tooltip : "Click if you want me to write more about this topic in the future.";
        const configMessageTitle = "messageTitle" in config ? config.messageTitle : "I Want To Read More";
        const configMessageText =
            "messageText" in config ? config.messageText : "Thank you! I will write more on this topic in the future!";
        const configMessageDuration = "messageDuration" in config ? config.messageDuration : 10;

        // Inject the toast (and delete the old one if needed)
        const oldToast = document.getElementById("iwanttoreadmore-vote-toast");
        if (oldToast) oldToast.remove();

        document.body.insertAdjacentHTML(
            "beforeend",
            `<div id="iwanttoreadmore-vote-toast"><h3>${configMessageTitle}</h3><p>${configMessageText}</p><small>Powered by <a href="https://iwanttoreadmore.com" target="_blank" rel="noopener">iwanttoreadmore.com</a></small></div>`
        );

        // Process all vote links
        document.querySelectorAll("[data-vote]").forEach((voteLink) => {
            // Add icon and set style
            voteLink.classList.add("iwanttoreadmore-vote-link");
            if (configVoteLink) voteLink.innerHTML = configVoteLink;
            voteLink.setAttribute("title", configTooltip);
            voteLink.setAttribute("aria-label", configTooltip);

            // Remove the tooltip if the tooltip is empty
            if (!configTooltip) voteLink.removeAttribute("data-vote");

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
                if (configMessageDuration > 0) {
                    const toast = document.getElementById("iwanttoreadmore-vote-toast");
                    toast.style.display = "block";
                    setInterval(function () {
                        toast.style.display = "none";
                    }, configMessageDuration * 1000);
                }

                return false;
            };
        });
    },
};

if (document.readyState !== "loading") {
    iwanttoreadmore.init();
} else {
    document.addEventListener("DOMContentLoaded", iwanttoreadmore.init);
}
