Title: Roadmap
Date: 2020-12-10
Slug: roadmap
save_as: roadmap.html

{% from 'iwrm_macros.j2' import vote %}
{% import 'icons.html' as icons %}

We want to develop [I Want To Read More](https://iwanttoreadmore.com) according to our users' needs. Here, you have the chance to vote for the features that you want to see implemented first. The voting is implemented with I Want To Read More voting links (of course 😄).

If there is a feature you are missing, you can create a request using [GitHub Discussions](https://github.com/haltakov/iwanttoreadmore/discussions?discussions_q=category%3AIdeas).

## Planned Features

-   Hide and delete of whole projects - {{ vote('haltakov', 'iwrm-roadmap', 'hide-delete-projects') }}
-   Plot the voting history over time - {{ vote('haltakov', 'iwrm-roadmap', 'see-voting-history') }}
-   Show votes for a project on a pie chart - {{ vote('haltakov', 'iwrm-roadmap', 'votes-chart') }}
-   Receive a weekly summary per e-mail - {{ vote('haltakov', 'iwrm-roadmap', 'email-summary') }}

## Current State

Here you can see a live widget with the current voting stats. You can see this on the [public dashboard](https://iwanttoreadmore.com/stats/haltakov) as well.

<div
    class="w-full lg:w-2/3 mx-auto mt-6 px-2 md:px-5 pb-2 pt-8 md:pt-4 bg-white rounded-lg shadow-lg relative"
>
    <h3 class="font-bold text-center" style="font-size: 1rem;"></h3>
    <button class="reload-button absolute right-0 top-0 mr-2 mt-2 animate-spin">
        {{ icons.reload("w-4") }}
    </button>
    <table class="w-full mt-6" id="template-table">
        <thead>
            <tr>
                <th scope="col" class="pb-3 text-left">Topic <button class="link text-sm">▼</button></th>
                <th scope="col" class="pb-3 text-right">Votes <button class="link text-sm">▼</button></th>
                <th scope="col" class="pb-3 text-center">
                    Last Vote <button class="link text-sm">▼</button>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td colspan="3" class="text-center h-64">{{ icons.dots("animate-pulse w-16 mx-auto") }}</td>
            </tr>
        </tbody>
    </table>
</div>

<script src="/theme/js/stats.js"></script>
<script>
    function init() {
        iwanttoreadmore.init({
            voteLink: 'vote <svg viewBox="0 0 22 27"><circle r="5" cx="11" cy="5"/><rect ry="1.5" x="3" y="9" height="18" width="16" style="stroke:#fff;stroke-width:1.5"/><ellipse rx="3" ry="4" cx="3" cy="18.5" style="stroke:#fff;stroke-width:2"/><ellipse rx="3" ry="4" cx="19" cy="18.5" style="stroke:#fff;stroke-width:2"/></svg>',
            tooltip: "Click to vote for this feature to be prioritized.",
            messageText: "Thank you for your feedback! This feature will be prioritized.",
        });

        loadVotes("haltakov", "iwrm-roadmap");
    }

    if (document.readyState !== "loading") {
        init();
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }
</script>
