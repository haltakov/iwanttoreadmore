/**
 * Fetch the votes for a user from the backend and load them in the table
 * @param user - name of the user
 * @param project - optional name of the user's project (if left empty, all projects for the given user are loaded)
 */
function loadVotes(user, project = "") {
    fetch(`/votes/${user}/${project || ""}`, {
        method: "GET",
        mode: "cors",
        credentials: "same-origin",
    }).then((response) => {
        if (response.ok)
            response.json().then((data) => {
                // Get list of all projects
                // TODO: Optmize by providing the data already split from the API
                const votes_data = data["votes"];
                const projects = new Set(votes_data.map((vote) => vote["project_name"]));

                // Create the tables for each project
                createProjectsTables(user, projects, data["single_voting_projects"]);

                // Populate the tables of each project with the data
                projects.forEach((project) =>
                    fillVotesTable(
                        user,
                        votes_data.filter((vote) => vote["project_name"] == project)
                    )
                );
            });
        else {
            document.getElementById("no-user-found-message").classList.remove("hidden");
            document.getElementById("template-table").parentElement.remove();
        }
    });
}

/**
 * Fill the votes table with the provided data
 * @param user - user whos dashboard is shown
 * @param votesData - votes data for the given project
 */
function fillVotesTable(user, votesData) {
    // Sort the data
    votesData.sort((first, second) => second.vote_count - first.vote_count);

    // Get the table for the corresponding project
    const table = document.getElementById(`table-${votesData[0].project_name}`);
    const tbody = table.getElementsByTagName("tbody")[0];

    // Set the table meta data
    table.setAttribute("data-user", user);
    table.setAttribute("data-project", votesData[0].project_name);

    // Clear all tables
    tbody.innerHTML = null;

    // Fill the table with the new data
    votesData.forEach((vote, i) => {
        const voteRow = document.createElement("tr");
        voteRow.classList.add("hover:bg-gray-200");

        if (vote.hidden) {
            voteRow.classList.add("hidden", "text-gray-500");
            voteRow.setAttribute("data-hidden", "");
        }

        voteRow.insertAdjacentHTML(
            "beforeend",
            `<td class="topic-cell py-1 pl-2" data-value=${vote.topic}>${vote.topic}</td>`
        );
        voteRow.insertAdjacentHTML(
            "beforeend",
            `<td class="pl-1 pr-2 text-right" data-value=${vote.vote_count}>${vote.vote_count}</td>`
        );
        voteRow.insertAdjacentHTML(
            "beforeend",
            `<td class="py-1 text-center" data-value="${vote.last_vote}">${timestampToDate(vote.last_vote)}</td>`
        );

        if (document.cookie.endsWith(`=${user}`)) {
            voteRow.insertAdjacentHTML(
                "beforeend",
                `<td>
                <button class="link vote-config">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </button>
                <div class="vote-config-menu absolute right-0 mr-3 hidden rounded-lg shadow-lg text-center text-gray-700 bg-white">
                    <button class="vote-config-hide rounded-lg rounded-b-none hover:bg-gray-200 uppercase text-sm font-bold border border-3 border-gray-400 w-32 p-2 block">Hide</button>
                    <button class="vote-config-show rounded-lg rounded-b-none hover:bg-gray-200 uppercase text-sm font-bold border border-3 border-gray-400 w-32 p-2 block hidden">Show</button>
                    <button class="vote-config-delete rounded-lg rounded-t-none hover:bg-gray-200 uppercase text-sm font-bold border border-3 border-gray-400 w-32 p-2 block border-t-0">Delete</button>
                </div>
            </td>`
            );
        } else {
            voteRow.insertAdjacentHTML("beforeend", `<td></td>`);
        }

        tbody.appendChild(voteRow);
    });

    // Init the vote menus
    initVoteMenus(table);

    // Stop spinning the reload button
    table.parentElement.getElementsByClassName("reload-button")[0].classList.remove("animate-spin");
}

/**
 * Create a table element for each project
 * @param user - user the projet belongs to
 * @param projects - list of the user's projects
 * @param single_voting_projects - list of the single voting projects
 */
function createProjectsTables(user, projects, single_voting_projects) {
    // Check it single_voting_projects is null
    if (!single_voting_projects) single_voting_projects = [];

    // Get the table that should be used as a template to create all other tables
    const templateTable = document.getElementById("template-table");

    // Check if tables were already created
    if (!templateTable) return;

    // Create the table for each project
    projects.forEach((project) => {
        // Copy the table container and set the title
        const tableDiv = templateTable.parentElement.cloneNode(true);
        tableDiv.querySelector("h3").innerHTML = project.toUpperCase();

        // Set the correct table ID
        const table = tableDiv.getElementsByTagName("table")[0];
        table.id = `table-${project}`;

        // Append to the list
        templateTable.parentElement.parentElement.appendChild(tableDiv);

        // Initialize buttons
        initSorting(table);
        initReloadButton(table, () => loadVotes(user, project));
        initSingleVotingCheckbox(table, project, single_voting_projects.includes(project));
    });

    // Display error message if no projects were found
    if (projects.size == 0) {
        // Check if this is a logged in user that has no votes yet
        if (document.cookie.endsWith(`=${user}`))
            document.getElementById("no-votes-message").classList.remove("hidden");
        else document.getElementById("no-user-found-message").classList.remove("hidden");
    }

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
 * Initialize the single voting project checkbox
 * @param table - node of the table for which the single voting project checkbox needs to be initialized
 * @param project - name of the project for which the checkbox is initialized
 * @param is_single_voting - True if the project is single voting and false otherwise
 */
function initSingleVotingCheckbox(table, project, is_single_voting) {
    const checkbox = table.parentElement.querySelector(".single-voting-project-checkbox");

    if (!checkbox) return;

    checkbox.parentElement.parentElement.parentElement.classList.remove("hidden");
    if (is_single_voting) checkbox.setAttribute("checked", "");

    checkbox.addEventListener("change", () => {
        if (checkbox.checked)
            fetch("/user/single_voting_project/add", {
                method: "POST",
                mode: "cors",
                credentials: "same-origin",
                body: project,
            });
        else
            fetch("/user/single_voting_project/remove", {
                method: "POST",
                mode: "cors",
                credentials: "same-origin",
                body: project,
            });
    });
}

/**
 * Initialize the vote menus
 * @param table - node of the table for which the menus need to be initialized
 */
function initVoteMenus(table) {
    const projectElement = table.parentElement;

    // Toggle the menu visibility
    projectElement.querySelectorAll(".vote-config").forEach((configLink) => {
        configLink.addEventListener("click", (event) => {
            const menu = configLink.parentElement.querySelector(".vote-config-menu");

            // Hide all other menus
            document.querySelectorAll(".vote-config-menu").forEach((element) => {
                if (element != menu) element.classList.add("hidden");
            });

            // Toggle the visibility
            if (menu.classList.contains("hidden")) menu.classList.remove("hidden");
            else menu.classList.add("hidden");

            // Choose the show or hide element
            if (configLink.parentElement.parentElement.hasAttribute("data-hidden")) {
                menu.querySelector(".vote-config-show").classList.remove("hidden");
                menu.querySelector(".vote-config-hide").classList.add("hidden");
            } else {
                menu.querySelector(".vote-config-show").classList.add("hidden");
                menu.querySelector(".vote-config-hide").classList.remove("hidden");
            }

            event.stopPropagation();

            return false;
        });
    });

    // Hide all menus on click on the page
    document.addEventListener("click", () => {
        document.querySelectorAll(".vote-config-menu").forEach((element) => {
            element.classList.add("hidden");
        });
    });

    // Handle a click of the hide button
    projectElement.querySelectorAll(".vote-config-hide").forEach((link) => {
        link.addEventListener("click", (event) => {
            const row = link.parentElement.parentElement.parentElement;

            row.classList.add("text-gray-500");
            row.setAttribute("data-hidden", "");

            if (projectElement.querySelector(".hide-hidden-link").classList.contains("hidden"))
                row.classList.add("hidden");

            const user = table.getAttribute("data-user");
            const project = table.getAttribute("data-project");
            const topic = row.querySelector(".topic-cell").getAttribute("data-value");
            fetch(`/votes/hidden/${user}/${project}/${topic}`, {
                method: "POST",
                mode: "cors",
                credentials: "same-origin",
                body: "1",
            });

            return false;
        });
    });

    // Handle a click of the show button
    projectElement.querySelectorAll(".vote-config-show").forEach((link) => {
        link.addEventListener("click", (event) => {
            const row = link.parentElement.parentElement.parentElement;

            row.classList.remove("text-gray-500");
            row.removeAttribute("data-hidden");
            row.classList.remove("hidden");

            const user = table.getAttribute("data-user");
            const project = table.getAttribute("data-project");
            const topic = row.querySelector(".topic-cell").getAttribute("data-value");
            fetch(`/votes/hidden/${user}/${project}/${topic}`, {
                method: "POST",
                mode: "cors",
                credentials: "same-origin",
                body: "0",
            });

            return false;
        });
    });

    // Handle a click of the delete button
    projectElement.querySelectorAll(".vote-config-delete").forEach((link) => {
        link.addEventListener("click", (event) => {
            const row = link.parentElement.parentElement.parentElement;

            const user = table.getAttribute("data-user");
            const project = table.getAttribute("data-project");
            const topic = row.querySelector(".topic-cell").getAttribute("data-value");
            fetch(`/votes/delete/${user}/${project}/${topic}`, {
                method: "POST",
                mode: "cors",
                credentials: "same-origin",
            });

            row.remove();

            return false;
        });
    });

    // Handle the Show hidden click
    projectElement.querySelectorAll(".show-hidden-link").forEach((link) => {
        link.addEventListener("click", () => {
            link.classList.add("hidden");
            link.parentElement.querySelector(".hide-hidden-link").classList.remove("hidden");

            link.parentElement.parentElement.querySelectorAll("tr[data-hidden]").forEach((row) => {
                row.classList.remove("hidden");
            });
        });
    });

    // Handle the Hide hidden click
    projectElement.querySelectorAll(".hide-hidden-link").forEach((link) => {
        link.addEventListener("click", () => {
            link.classList.add("hidden");
            link.parentElement.querySelector(".show-hidden-link").classList.remove("hidden");

            link.parentElement.parentElement.querySelectorAll("tr[data-hidden]").forEach((row) => {
                row.classList.add("hidden");
            });
        });
    });
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
