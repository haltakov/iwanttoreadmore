/**
 * Initializes all UI elements
 */
function init() {
    // Choose which navbar to show
    chooseNavbar();

    // Init the highlight.js library
    hljs.initHighlightingOnLoad();

    // Init the logout button
    initLogoutButton();
}

/**
 * Chooses which navbar to show depending on if the user is loggen in or not and sets the link to the user dashboard
 */
function chooseNavbar() {
    if (document.cookie.includes("loggedinuser")) {
        document.getElementById("logged-out-nav").classList.add("hidden");
        document.getElementById("logged-in-nav").classList.remove("hidden");

        // Set the link to the user dashboard
        const username = document.cookie.split("=").pop();
        document.getElementById("nav-dashboard-link").href = `/stats/${username}`;
    }
}

/**
 * Deletes the loggedin cookie when the logout button is clicked
 */
function initLogoutButton() {
    const logoutButton = document.getElementById("logout-button");
    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            document.cookie = "loggedinuser=; Path=/; Max-Age=-99999999;";
            document.location = logoutButton.href;
        });
    }
}

/**
 * Check if the user is logged in by making an API request and redirect to the login page if not
 * @param {*} successCallback function to call if successful
 */
function checkUserLogged(successCallback) {
    fetch("/user/loggedin", {
        method: "GET",
        mode: "cors",
        credentials: "same-origin",
    })
        .then((response) => {
            if (response.ok) successCallback();
            else document.location = "/login";
        })
        .catch((error) => (document.location = "/login"));
}

/**
 * Check if the user is logged in by looking at the cookies and redirect to the login page if not
 * @param {*} successCallback function to call if successful
 */
function checkUserLoggedFast(successCallback) {
    if (document.cookie.includes("loggedinuser")) successCallback();
    else document.location = "/login";
}

/**
 * Display an error message in the flash
 * @param {*} flashElement
 * @param {*} message
 */
function displayError(flashElement, message) {
    flashElement.innerHTML = message;
    flashElement.classList.add("flash-error");
    flashElement.classList.remove("hidden");
}

/**
 * Display a success message in the flash
 * @param {*} flashElement
 * @param {*} message
 */
function displaySuccess(flashElement, message) {
    flashElement.innerHTML = message;
    flashElement.classList.add("flash-success");
    flashElement.classList.remove("hidden");
}

/**
 * Form initialization helper that will submit the data to the API
 * @param {*} formId ID of the form element
 * @param {*} url URL to submit the form to
 * @param {*} responseCallback function to be called when the response is received
 * @param {*} flashId ID of the flash element (default "flash")
 * @param {*} buttonActiveClass class to use for an active submit button. If "" the function will try to infer the class by itself (default "")
 * @param {*} buttonDisabledClass class to use for a disabled submit button (default "button-disabled")
 */
function initAjaxForm(
    formId,
    url,
    responseCallback,
    flashId = "flash",
    buttonActiveClass = "",
    buttonDisabledClass = "button-disabled"
) {
    // Get the form, the submit button and the flash id
    const form = document.getElementById(formId);
    const submitButton = form.querySelector('button[type="submit"]');
    const flash = document.getElementById(flashId);

    // Try to estimate the buttonActiveClass if not provided
    if (!buttonActiveClass) {
        const buttonClasses = Array.from(submitButton.classList).filter((c) => c.startsWith("button-"));
        if (buttonClasses.length > 0) buttonActiveClass = buttonClasses[0];
    }

    // Add a spinner to the submit button
    submitButton.innerHTML =
        '<span><svg class="w-5 mr-2 inline animate-spin hidden" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg></span> ' +
        submitButton.innerHTML;
    const submitButtonSpinner = submitButton.querySelector("svg");

    // Handle the form submission
    form.onsubmit = () => {
        // Clear and hide the flash
        flash.innerHTML = "";
        flash.classList.add("hidden");
        flash.classList.remove("flash-success");
        flash.classList.remove("flash-error");

        // Disable the button
        submitButton.classList.remove(buttonActiveClass);
        submitButton.classList.add(buttonDisabledClass);
        submitButtonSpinner.classList.remove("hidden");

        // Collect the form content from the inputs
        const formContent = Array.from(form.getElementsByTagName("input"))
            .map((element) => `${element.name}=${element.value}`)
            .join(";");

        // Submit the form
        fetch(url, {
            method: "POST",
            mode: "cors",
            credentials: "same-origin",
            body: formContent,
        }).then((response) => {
            responseCallback(response, flash);

            // Enable the button again
            submitButton.classList.add(buttonActiveClass);
            submitButton.classList.remove(buttonDisabledClass);
            submitButtonSpinner.classList.add("hidden");
        });

        return false;
    };
}

if (document.readyState !== "loading") {
    init();
} else {
    document.addEventListener("DOMContentLoaded", init);
}
