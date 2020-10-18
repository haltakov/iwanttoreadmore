/**
Fetch the votes from the backend and load them in the table
*/
function loadVotes() {
    fetch("https://iwanttoreadmore.com/votes/haltakov/iwanttoreadmore")
        .then((response) => response.json())
        .then((data) => {
            fillVotesTable(data);
        });
}

/**
 * Adds a leading zero to single digit numbers
 * @param {int} x - number
 * @return padded string
 */
function padZero(x) {
    return (x < 10 ? "0" : "") + x;
}

/**
 * Converts a UTC timestamp to a date string
 * @param {float} votesData - votes data
 * @return date string
 */
function timestampToDate(timestamp) {
    const voteDateTime = new Date(timestamp * 1000);
    let day = padZero(voteDateTime.getDate());
    let month = padZero(voteDateTime.getMonth() + 1);
    let year = voteDateTime.getFullYear();
    let hours = padZero(voteDateTime.getHours());
    let minutes = padZero(voteDateTime.getMinutes());

    const fullDateString = `${day}.${month}.${year} ${hours}:${minutes}`;

    const voteDate = new Date(voteDateTime).setHours(0, 0, 0, 0);
    const currentDate = new Date().setHours(0, 0, 0, 0);
    const daysDiff = Math.floor((currentDate - voteDate) / (24 * 60 * 60 * 1000));

    var dateString = "";
    if (daysDiff == 0) dateString = `Today ${hours}:${minutes}`;
    else if (daysDiff == 1) dateString = `Yesterday`;
    else if (daysDiff < 7) dateString = `${daysDiff} days ago`;
    else dateString = `${day}.${month}.${year}`;

    return `<span title="${fullDateString}" data-toggle="tooltip" data-placement="right">${dateString}</span>`;
}

/**
 * Fill the votes table with the provided data
 * @param {JSON} votesData - votes data
 */
function fillVotesTable(votesData) {
    // Sort the data
    votesData.sort((first, second) => second.vote_count - first.vote_count);

    // Clear all tables
    document.querySelectorAll("tbody").forEach((x) => (x.innerHTML = null));

    // Fill the table with the new data
    votesData.forEach((vote, i) => {
        const tableId = `table-${vote.project_name}`;

        const voteRow = document.createElement("tr");
        voteRow.classList.add("hover:bg-gray-200");
        voteRow.insertAdjacentHTML("beforeend", `<td class="py-1 pl-2">${vote.topic}</td>`);
        voteRow.insertAdjacentHTML("beforeend", `<td class="py-1 text-right">${vote.vote_count}</td>`);
        voteRow.insertAdjacentHTML("beforeend", `<td class="py-1 text-center">${timestampToDate(vote.last_vote)}</td>`);

        document.querySelector(`#${tableId} tbody`).appendChild(voteRow);
    });

    // Stop spinning the reload buttons
    reloadButtons = Array.from(document.getElementsByClassName("reload-button"));
    reloadButtons.forEach((e) => e.classList.remove("animate-spin"));
}

/**
 * Initialize the reload buttons
 */
function initReloadButtons() {
    reloadButtons = Array.from(document.getElementsByClassName("reload-button"));
    reloadButtons.forEach((e) =>
        e.addEventListener(
            "click",
            (event) => {
                e.classList.add("animate-spin");
                loadVotes();
            },
            true
        )
    );
}

/**
 * Initializing the sorting function for each column of the table
 */
function initSorting() {
    const getCellValue = (tr, idx) => {
        console.log(tr.children[idx].innerHTML);
        return tr.children[idx].innerHTML;
    };

    const comparer = (idx, desc) => (a, b) =>
        ((v1, v2) => (v1 !== "" && v2 !== "" && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)))(
            getCellValue(desc ? b : a, idx),
            getCellValue(desc ? a : b, idx)
        );

    document.querySelectorAll("th a").forEach((a) =>
        a.addEventListener("click", () => {
            const table = a.closest("table").querySelector("tbody");
            Array.from(table.querySelectorAll("tr:nth-child(n+1)"))
                .sort(
                    comparer(
                        Array.from(a.parentNode.parentNode.children).indexOf(a.parentNode),
                        (this.desc = !this.desc)
                    )
                )
                .forEach((tr) => table.appendChild(tr));
        })
    );
}

if (document.readyState !== "loading") {
    loadVotes();
    initSorting();
    initReloadButtons();
} else {
    document.addEventListener("DOMContentLoaded", loadVotes);
    document.addEventListener("DOMContentLoaded", initSorting);
    document.addEventListener("DOMContentLoaded", initReloadButtons);
}
