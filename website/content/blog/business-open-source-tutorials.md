Title: Building a product in the open: open source, open metrics, open development.
Date: 2020-07-05
Slug: building-a-product-in-the-open
Image: building-open-cover.jpg
Summary: I had this idea, when I started my personal blog couple of months ago. I was writing on different topics like self-driving cars, technology and travel. Sometimes, I touched on topics about which I could write a whole new article. I had so many ideas, but how to decide, what to write about next? Wouldn't it be nice if I could just ask my readers?

## The Idea

{% from 'iwrm_macros.j2' import vote %}

I had this idea, when I started my [personal blog](https://haltakov.net/blog) couple of months ago. I was writing on different topics like self-driving cars, technology and travel. Sometimes, I touched on topics about which I could write a whole new article. I had so many ideas, but how to decide, what to write about next? Wouldn't it be nice if I could just ask my readers?

I started adding small icons like this {{ vote("haltakov","iwanttoreadmore","example") }} at suitable places in the text. The idea was that if a reader was interested about this topic, he could just click the icon to vote for it. No registration required, no filling of feedback forms - just a single click! This worked well and people reading my blog started clicking the vote links. There were some real surprises, about which topics people found interesting.

For example, I wrote an article about [travel planning](https://haltakov.net/blog/travel-planning/). My plan was to write a follow-up article about organizing the time during the trip. However, most people voted that they want to read about traveling with a baby instead and this is what I ended up [writing about](https://haltakov.net/blog/flying-with-baby/) next.

<div class="d-md-flex justify-content-center flex-wrap my-4">
  <div>
    <a href="https://haltakov.net/blog/travel-planning/" target="_blank">
        <img class="m-2 image-500 shadow" src="{{ SITEURL }}/images/building-open-blog-example.jpg" alt="Example vote link in Vladimir Haltakov's blog">
    </a>
    <p class="text-center">Vote link in one of the articles in my blog - most people clicked this one.</p>
  </div>
</div>

## The Prototype

I didn't want to spend too much time coding a tool, before I knew that it will be useful. So, I found a nice way to set the whole thing up with a minimal effort, even if it was a hack...

I use a static site generator for my blog ([Pelican](https://blog.getpelican.com/)) and host it on [Netlify](https://www.netlify.com/). This means that I didn't have a server where I could run code and a database to store the results. I also didn't want to set the whole thing up before I knew it is worth it. However, I made use of two features that Netlify offers - custom [redirect rules](https://docs.netlify.com/routing/redirects/) and server side [analytics](https://www.netlify.com/products/analytics/).

When somebody clicks a vote link, a simple JavaScript code would just make a GET request to a URL like that `https://haltakov.net/iwanttoreadmore/some-topic`. I created a rule that would redirect such requests it to an empty page {{ vote("haltakov","iwanttoreadmore","netlify-redirect") }}. The result is not shown to the user - he will only see is a small toast that the vote is counted.

In the server side analytics, though, the original URL is counted every time somebody clicked on the vote link. I could then just look at the open counts for the `iwanttoreadmore` URLs and see which topics are more popular. In practice, getting the information was a bit cumbersome, because Netlify's analytics page only allows you to see the 15 URLs with the most visits. However, it fetches the data from a REST API, so I was able to call it with different parameters and get all the data {{ vote("haltakov","iwanttoreadmore","netlify-analytics") }} (thanks [Jim Nielsen](https://blog.jim-nielsen.com/2020/using-netlify-analytics-to-build-list-of-popular-posts/)). In the end, I had statistics about which topics my readers found most interesting, which I used to decide which topics I should write about on my blog.

<div class="d-md-flex justify-content-center flex-wrap my-4">
  <div>
    <a href="{{ SITEURL }}/images/building-open-netlify-stats.jpg" target="_blank">
        <img class="m-2 image-500 shadow" src="{{ SITEURL }}/images/building-open-netlify-stats.jpg" alt="Netlify statistics for the first I Want To Read More prototype.">
    </a>
    <p class="text-center">Netlify statistics for the vote links.</p>
  </div>
</div>

## The Product

I thought that if this tool is so useful to me, it may be useful to other bloggers as well. So, I started building as a real web service on [iwanttoreadmore.com](https://iwanttoreadmore.com). I decided to build this project in the open {{ vote("haltakov","iwanttoreadmore","build-in-the-open") }} and I have set myself the following goals for it:

-   **Open source**. I will open source all the code on [GitHub](https://github.com/haltakov/iwanttoreadmore).
-   **Open metrics**. I will make all the metrics and statistics public, starting with the [web analytics](https://plausible.io/iwanttoreadmore.com).
-   **Open development**. I will write about how I make all important decisions during the development in [this blog](https://iwanttoreadmore.com/blog).
-   **Simple**. I will keep it as simple and as easy to use as possible.
-   **Privacy oriented**. I will only collect the data needed to count the votes and nothing else (not even IP addresses) and will not be sold.
-   **Paid service**. It will be a paid service so my incentives will be aligned with those of my customers - providing the best product for them and not for advertisers.

## The Experiment

I benefited a lot from the indie hackers community and I want to give back to it. While building this project I'm learning many new things, so will write a tutorial for every major feature I implement (you can start with the first one for [creating a static site with Pelican]({{ SITEURL }}/blog/building-a-product-in-the-open/)). There I will share why I chose specific design or technology and the steps to build it. The tutorials will use the exact same code I use to run the product. And of course, I will use [I Want To Read More](https://iwanttoreadmore.com) to get feedback on what topics to write about 😃.
