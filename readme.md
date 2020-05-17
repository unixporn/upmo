# u/upmo

[u/upmo](https://www.reddit.com/user/upmo) (UnixPornMOderator) was a [Reddit](https://reddit.com) bot written to automate some of the more menial tasks in subreddit moderation. In April 2020 upmo was replaced by automoderator for long term simplicity and maintainability. It won't recieve further updates to keep pace with [PRAW](https://praw.readthedocs.io/en/latest/) but you're still free to reuse the code under the MIT license.

Most of the functions originally come from a [collection of small bots](https://github.com/voussoir/reddit) written by [u/GoldenSights](https://www.reddit.com/user/Goldensights) for various different subreddits. From there they were reworked, merged and heavily modified to create what I thought a bot should be. The major changes are the addition of timed responses and the use of a single text file instead of multiple SQL databases for history management.

Within [r/unixporn](https://www.reddit.com/r/unixporn) it carried out the following duties:

* Removes posts using deprecated tags
* Removes posts using OS tags
* Removes posts without DE tagged in title
* Assigns correct link flair to posts
* Checks links are through approved hosts
* Warns user if they haven't added a details comment after 15 minutes
* Removes posts which haven't added a details comment after 30 minutes
* Removes posts if the user doesn't meet the minimum karma requirements
