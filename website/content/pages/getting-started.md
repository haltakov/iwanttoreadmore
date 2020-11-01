Title: Getting started
Date: 2020-11-01
Slug: getting-started

## Introduction

I Want To Read More provides you with a script that will find all the vote links in your text, display the voting icon and create all the required events to handle to voting logic and the UI.

## Setup

To start using I Want To Read More you need to include the CSS and JavaScript files in your HTML.

-   Include the CSS in the `<head>` section:
<pre><code class="language-html">&lt;link rel="stylesheet" href="https://iwanttoreadmore.com/dist/iwanttoreadmore.css" /&gt;
</code></pre>

-   Include the JavaScript right before the closing `</body>` tag, but before the script from which you will call the initialization function:
<pre><code class="language-html">&lt;script defer src="https://iwanttoreadmore.com/dist/iwanttoreadmore.js"&gt;&lt;/script&gt;
</code></pre>

-   Call the initliazing function when your page is loaded:
<pre><code class="language-js">iwanttoreadmore.init();
</code></pre>

## Adding Vote Links

To add a vote link to your text add a regular `<a>` tag with a `data-vote` attribute:

<pre><code class="language-html">&lt;a href="#" data-vote="username/project/topic"&gt;&lt;/a&gt;
</code></pre>

The `data-vote` attribute consists of the following parameters:

-   `username` - this is your user name for I Want To Read More
-   `project` - this is the name of your project at I Want To Read More
-   `topic` - this is the topic that you want to setup the voting for
