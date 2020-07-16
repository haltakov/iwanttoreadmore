/**
 * Initializes all UI elements
 */
function init() {
    $('[data-toggle="tooltip"]').tooltip();

    $(".toast").on("show.bs.toast", function () {
        $(this).removeClass("d-none");
    });
    $(".toast").on("hidden.bs.toast", function () {
        $(this).addClass("d-none");
    });

    Array.from(document.querySelectorAll("[data-vote]")).forEach(
        (e) =>
            (e.onclick = (event) => {
                const url = `https://iwanttoreadmore.com/vote/${e.getAttribute("data-vote")}`;
                fetch(url, { method: "post" });

                e.removeAttribute("href");
                e.onclick = null;
                e.querySelector("svg").classList.remove("vote-link");
                $('[data-toggle="tooltip"]').tooltip("hide");

                $(".toast").toast("show");

                return false;
            })
    );
}

if (document.readyState !== "loading") {
    init();
} else {
    document.addEventListener("DOMContentLoaded", init);
}
