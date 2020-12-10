Title: Getting started
Date: 2020-12-10
Slug: getting-started

{% from 'iwrm_macros.j2' import vote %}

## Introduction

I Want To Read More is a service that allows you to integrate vote links in your blog. Your readers can click on these links if they are interested in a particular topic and you will see the aggregated statistics in your dashboard.

There are several different ways to integrate the vote links, depending on how much control you have on your blog (for example if you are able to run JavaScript) and how much customization you want to do:

-   [Minimal setup](#minimal-setup) - no JavaScript or CSS required. Easy integration into any blogging platform.
-   [Advanced setup](#advanced-setup) - you need to include our JavaScript and CSS, but you get a better user experience.
-   [Custom setup](#customize-setup) - you can easily customize every part of the UI/UX if you want to.

## Projects and Topics

Take a minute to uderstand the concept of **projects** and **topics** before you go on. Every vote link has the following 3 components which you will need to specify:

-   `username` - this is your user name for I Want To Read More
-   `project` - this is the name of your project
-   `topic` - this is the topic that you want to setup the voting for

The project is a collection of multiple topics so that you can organize them better. You can create one project for every article you write or you can use one for your entire blog. This is up to your preferences! The first time somebody clicks a vote link, it will automatically appear in your dashboard.

<a name="minimal-setup"></a>

## Minimal Setup

The minimal setup is just to include direct links to the vote API. When the user clicks on a link he will be taken to a page with a simple "Thank you for voting" message. The message itself or the page can be [customized](#voted-message-customization).

You can easily use way of integration on any blogging platform, like for example Hashnode (see [example](https://haltakov.hashnode.dev/i-want-to-read-more-demo)), Dev.to (see [example](https://dev.to/haltakov/i-want-to-read-more-demo-b1b)) or Wordpress (see example), because it doesn't require you to include any JavaScript or CSS. However, in this way a new page will open up instead of showing a toast.

<pre><code class="language-text">https://iwanttoreadmore.com/vote/&lt;usernamee&gt;/&lt;project&gt;/&lt;topic&gt;/</code></pre>

Here is how it looks like if you are using Markdown:

<pre><code class="language-markdown">[Vote](https://iwanttoreadmore.com/vote/&lt;usernamee&gt;/&lt;project&gt;/&lt;topic&gt;/)</code></pre>

In many platforms, you can also use HTML directly:

<pre><code class="language-html">&lt;a href="https://iwanttoreadmore.com/vote/&lt;usernamee&gt;/&lt;project&gt;/&lt;topic&gt;/" target="_blank" rel="noopener"&gt;Vote&lt;/a&gt;</code></pre>

<a name="voted-message-customization"></a>

### Customizing the message after voting

You can customize the message that the reader will see after voting from the [Settings](https://iwanttoreadmore.com/settings) page. Alternatively, you can also specify a page on your onw website, where the user will be redirected after voting. We just ask you to include a small text that the voting is powered by [iwanttoreadmore.com](https://iwanttoreadmore.com).

<a name="advanced-setup"></a>

## Advanced Setup

If you are able to include JavaScript and CSS files in your blog, you will be able to improve the user experience by showing a toast with information when a reader clicks on the vote link, instead of opening a new page. The vote links will also show as small icons like this {{ vote("haltakov","iwanttoreadmore","example") }} in the text.

1.  Include the CSS in the `<head>` section:
<pre><code class="language-html">&lt;link rel="stylesheet" href="https://iwanttoreadmore.com/dist/iwanttoreadmore.min.css" /&gt;
</code></pre>

2.  Include the JavaScript right before the closing `</body>` tag, but before the script from which you will call the initialization function:
<pre><code class="language-html">&lt;script defer src="https://iwanttoreadmore.com/dist/iwanttoreadmore.min.js"&gt;&lt;/script&gt;
</code></pre>

3.  Call the initliazing function when your page is loaded:
<pre><code class="language-js">iwanttoreadmore.init();
</code></pre>

4.  To add a vote link to your text add a regular `<a>` tag with a `data-vote` attribute:

<pre><code class="language-html">&lt;a href="#" data-vote="<username>/<project>/<topic>"&gt;&lt;/a&gt;
</code></pre>

### Configuration options

You can initialize the script without any parameters to use the defaults, but you can also configure the messages and the icon of the vote links. You have the following options:

-   `voteLink` - content of the vote link (by default the I Want To Read More icon). HTML can be used. Set to empty to use the original content of the link.
-   `tooltip` - text to show in the tooltip. Set to empty to hide the tooltip.
-   `messageTitle` - title of the message shown after voting
-   `messageText` - text of the message shown after voting
-   `messageDuration` - duration that the message will be shown after voting in seconds. Set to 0 to disable.

<a name="custom-setup"></a>

## Custom Setup

If you don't like the icon, the messages or the design of the toast, you can easily change them! Copy the [`iwanttoreadmore.js`](https://github.com/haltakov/iwanttoreadmore/blob/master/website/content/dist/iwanttoreadmore.js) and [`iwanttoreadmore.css`](https://github.com/haltakov/iwanttoreadmore/blob/master/website/content/dist/iwanttoreadmore.js) files to your server and adapt them as needed. Remember - everything is open-source! Some customization options in the initialization function of the script are [planned](https://github.com/haltakov/iwanttoreadmore/issues/60) for the near future.

## Need more help?

If you need any further help, you can contact us directy at the e-mail you will find at the top of the [Settings](https://iwanttoreadmore.com/settings) page.
