/**
 * Fetch the votes for a user from the backend and load them in the table
 * @param user - name of the user
 * @param project - optional name of the user's project (if left empty, all projects for the given user are loaded)
 */
function loadVotes(user, project = "") {
    fetch(`https://iwanttoreadmore.com/votes/${user}/${project || ""}`)
        .then((response) => response.json())
        .then((data) => {
            // Get list of all projects
            // TODO: Optmize by providing the data already split from the API
            const projects = new Set(data.map((vote) => vote["project_name"]));

            // Create the tables for each project
            createProjectsTables(user, projects);

            // Populate the tables of each project with the data
            projects.forEach((project) => fillVotesTable(data.filter((vote) => vote["project_name"] == project)));
        });
}

/**
 * Fill the votes table with the provided data
 * @param votesData - votes data for the give project
 */
function fillVotesTable(votesData) {
    // Sort the data
    votesData.sort((first, second) => second.vote_count - first.vote_count);

    // Get the table for the corresponding project
    const table = document.getElementById(`table-${votesData[0].project_name}`);
    const tbody = table.getElementsByTagName("tbody")[0];

    // Clear all tables
    tbody.innerHTML = null;

    // Fill the table with the new data
    votesData.forEach((vote, i) => {
        const voteRow = document.createElement("tr");
        voteRow.classList.add("hover:bg-gray-200");
        voteRow.insertAdjacentHTML("beforeend", `<td class="py-1 pl-2" data-value=${vote.topic}>${vote.topic}</td>`);
        voteRow.insertAdjacentHTML(
            "beforeend",
            `<td class="pl-1 pr-2 text-right" data-value=${vote.vote_count}>${vote.vote_count}</td>`
        );
        voteRow.insertAdjacentHTML(
            "beforeend",
            `<td class="py-1 text-center" data-value="${vote.last_vote}">${timestampToDate(vote.last_vote)}</td>`
        );

        tbody.appendChild(voteRow);
    });

    // Stop spinning the reload button
    table.parentElement.getElementsByClassName("reload-button")[0].classList.remove("animate-spin");
}

/**
 * Create a table element for each project
 * @param projects - list of the user's projects
 */
function createProjectsTables(user, projects) {
    // Get the table that should be used as a template to create all other tables
    const templateTable = document.getElementById("template-table");

    // Check if tables were already created
    if (!templateTable) return;

    // Create the table for each project
    projects.forEach((project) => {
        // Copy the table container and set the title
        const tableDiv = templateTable.parentElement.cloneNode(true);
        tableDiv.getElementsByTagName("h3")[0].innerHTML = project.toUpperCase();

        // Set the correct table ID
        const table = tableDiv.getElementsByTagName("table")[0];
        table.id = `table-${project}`;

        // Append to the list
        templateTable.parentElement.parentElement.appendChild(tableDiv);

        // Initialize buttons
        initSorting(table);
        initReloadButton(table, () => loadVotes(user, project));
    });

    templateTable.parentElement.remove();
}

/**
 * Initializing the sorting function for each column of a table
 * @param table - node of the table that needs to be sorted
 */
function initSorting(table) {
    const getCellValue = (tr, idx) => {
        return tr.children[idx].getAttribute("data-value");
    };

    const comparer = (idx, desc) => (a, b) =>
        ((v1, v2) => (v1 !== "" && v2 !== "" && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)))(
            getCellValue(desc ? b : a, idx),
            getCellValue(desc ? a : b, idx)
        );

    table.querySelectorAll("th button").forEach((button) => {
        button.desc = true;
        button.addEventListener("click", () => {
            const tableBody = table.querySelector("tbody");
            Array.from(tableBody.querySelectorAll("tr:nth-child(n+1)"))
                .sort(
                    comparer(
                        Array.from(button.parentNode.parentNode.children).indexOf(button.parentNode),
                        (button.desc = !button.desc)
                    )
                )
                .forEach((tr) => tableBody.appendChild(tr));
        });
    });
}

/**
 * Initialize the reload button for a table
 * @param table - node of the table for which the sort button needs to be initialized
 * @param loadVotes - function used to load the votes for the given table
 */
function initReloadButton(table, loadVotes) {
    const reloadButton = table.parentElement.getElementsByClassName("reload-button")[0];
    reloadButton.addEventListener(
        "click",
        (event) => {
            reloadButton.classList.add("animate-spin");
            loadVotes();
        },
        true
    );
}

/**
 * Adds a leading zero to single digit numbers
 * @param x - number
 * @return padded string
 */
function padZero(x) {
    return (x < 10 ? "0" : "") + x;
}

/**
 * Converts a UTC timestamp to a date string
 * @param votesData - votes data
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
    if (daysDiff == 0) dateString = `${hours}:${minutes}`;
    else if (daysDiff == 1) dateString = `Yesterday`;
    else if (daysDiff < 7) dateString = `${daysDiff} days ago`;
    else dateString = `${day}.${month}.${year}`;

    return `<span title="${fullDateString}" data-toggle="tooltip" data-placement="right">${dateString}</span>`;
}
