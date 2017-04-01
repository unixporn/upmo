#!/usr/bin/python3

# This is a modification and merge of several reddit bots
# written by /u/GoldenSights for various subs. This is an
# AutoMod bot which scans /r/unixporn for new posts while
# making sure that the rules are being followed. All work
# is licensed under the MIT License, without any warranty

# Required modules
from sys import stdout
from time import sleep
from getpass import getpass
from datetime import datetime, timezone
from praw import errors, helpers, Reddit


"""CONFIGURATION"""

# Bot's Username
USERNAME = "USERNAME"
# Sub to scan for new posts
SUBREDDIT = "SUBREDDIT"
# Short description of what the bot does
USERAGENT = "Automated moderator for /r/" + SUBREDDIT

# How many posts to retrieve at once (max 100)
MAXPOSTS = 10
# How many seconds to wait between running cycles. Bot is
# inactive during this time.
WAIT = 60
# Time before post is removed
DELAY = 1800
# Toggles whether bot reports before removal
TRUSTME = True

# Reddit URL
RURL = "https://www.reddit.com/"
# Direct link to send mod mail
MODMSG = RURL + "message/compose?to=%2Fr%2F" + SUBREDDIT
# Direct link for information about hosting
HOSTLINK = "{0}r/{1}/wiki/info/rules#wiki_2.0_-_hosting"
HOSTLINK = HOSTLINK.format(RURL, SUBREDDIT)
# Direct link for information about post categories
CATLINK = "{0}r/{1}/wiki/info/rules#wiki_3.0_-_categorisation"
CATLINK = CATLINK.format(RURL, SUBREDDIT)
# Markdown formatted link for details comment template
TEMPLATE = "[details comment]({0}r/{1}/wiki/info/template)"
TEMPLATE = TEMPLATE.format(RURL, SUBREDDIT)


def fillout(list):
    """
    Takes a list of strings as input and returns a list of tags using a
    variety of brackets & seperators
    """

    openers = ["[", "(", "{", "⟨"]
    closers = ["]", ")", "}", "⟩"]
    seperators = ["|", "·", "+", "/", "\\"]
    newlist = []
    for item in list:
        for opener in openers:
            closer = closers[openers.index(opener)]
            toadd = [opener + item + closer,
                     opener + " " + item + " " + closer]
            for seperator in seperators:
                toadd += [opener + item + seperator,
                          seperator + item + closer,
                          opener + " " + item + " " + seperator,
                          seperator + " " + item + " " + closer]
            newlist += toadd
    return newlist

# Website Whitelist
WHITELIST = ["g.redditmedia.com", "i.redd.it", "i.reddituploads.com",
             "imgur.com",
             "minus.com", "min.us",
             "gfycat.com",
             "pub.iotek.org",
             "u.teknik.io", "upload.teknik.io", "v.teknik.io",
             "mediacru.sh",
             "redditmetrics.com/r/unixporn"]

# Workflow extensions
EXTENSIONS = [".webm", ".gif", "gfycat", ".mp4"]

# Strings for the "Hardware" flair
HWSTRING = ["[desktop]",
            "[laptop]",
            "[multi]",
            "[phone]",
            "[portable]",
            "[server]",
            "[tablet]"]

# Title tags which shouldn't be used
TAGSTRING = ["discussion", "discussions",
             "hardware",
             "help", "request",
             "material", "materials",
             "meta",
             "mod",
             "other",
             "question", "q",
             "screenshot", "screenshots",
             "thread", "threads",
             "unixporn",
             "workflow",
             "wm/de", "wm", "de"]
TAGSTRING = fillout(TAGSTRING)

# Banned OS title tags
OSSTRING = ["aix",
            "android", "androidx86", "android x86",
            "arch", "archlinux", "arch linux",
            "bodhi",
            "bsd",
            "centos",
            "chakra",
            "crunchbang", "#!",
            "crux",
            "debian", "debian testing",
            "dragonflybsd",
            "eos", "elementary", "elementaryos", "elementary os",
            "exherbo",
            "fedora",
            "freebsd",
            "funtoo",
            "gentoo",
            "hurd", "gnu/hurd",
            "korora",
            "kubuntu",
            "lfs", "linux", "gnu/linux",
            "linux mint", "linuxmint", "mint", "lmde",
            "lubuntu",
            "manjaro",
            "netbsd",
            "nixos",
            "openbsd",
            "opensuse",
            "parabola",
            "plan9",
            "slackware",
            "ubuntu", "ubuntu gnome", "ubuntugnome",
            "windows", "windows 7", "windows 10", "win32",
            "xubuntu"]
OSSTRING = fillout(OSSTRING)

# Message about reporting bot errors
CONTACT = "\n\n*^[Contact]({0}) ^[us]({0}) ^if ^our ^bot ^has ^messed " \
          "^up*".format(MODMSG)

# Message when haven't added a details comment
NODETAILS = "You have not provided a {0} so the post has been removed. " \
            "Please add one and message the mod team so we can approve " \
            "your post.{1}".format(TEMPLATE, CONTACT)

# Message when not using a tag
NOTAGREPLY = "Your post appears to be missing a title [tag] so has " \
             "been removed. See [section 3]({0}) for more details but " \
             "briefly:\n\n* Screenshots requires [WM/DE]\n\n* Workflow " \
             "requires [WM/DE]\n\n* Hardware requires [DEVICE]\n\n" \
             "* Material requires [OC]{1}".format(CATLINK, CONTACT)

# Message when using a deprecated tag
DEPTAGREPLY = "Your post appears to be using one of the deprecated " \
              "[tags] so has been removed. The bot will automatically " \
              "apply the relevant link flair to posts." + CONTACT

# Message when stating OS in a title tag
OSREPLY = "Your post appears to be using the OS [tag] so has been " \
          "removed. This is now deprecated in favour of userflair." + CONTACT

# Message when not using an approved host
HOSTRESPONSE = "You don't appear to be using an [approved host]({0}) " \
               "so your post has been removed. Please resubmit using " \
               "one of them, but feel free to leave mirrors to host " \
               "in your details comment.{1}"
HOSTRESPONSE = HOSTRESPONSE.format(HOSTLINK, CONTACT)

# Warning when haven't added a details comment
DETAILSWARN = "Please add a {0}.{1}".format(TEMPLATE, CONTACT)

print(SUBREDDIT, "bot\n")


"""BOT LOGIN"""

r = Reddit(USERAGENT)
while True:
    try:
        PASSWORD = getpass("Password: ")
        r.login(USERNAME, PASSWORD)
        print("Successfully logged in\n")
        break
    except errors.InvalidUserPass:
        print("Wrong Username or Password\n")
        quit()
    except Exception as e:
        print("%s" % e)
        sleep(5)


"""DEFINING FUNCTIONS"""

def slay(post, response):
    print("\tReplying to OP")
    res = post.add_comment(response)
    res.distinguish()
    if TRUSTME is False:
        post.report()
    post.remove(spam=False)
    print("\tPost removed")
    sleep(5)


def tag_check(post, ptitle):
    print("Checking tags...")
    if any(key.lower() in ptitle for key in TAGSTRING):
        slay(post, DEPTAGREPLY)
    elif any(key.lower() in ptitle for key in OSSTRING):
        slay(post, OSREPLY)
    elif any(tag in ptitle for tag in ["[", "]"]) or post.is_self is True:
        pass
    else:
        slay(post, NOTAGREPLY)


def flair_assign(post, purl, ptitle, flair):
    print("Scanning for flairs...")
    if flair == "":
        print("\tNo Flair")
        if "[oc]" in ptitle:
            print("\tAssigning 'Material' flair")
            post.set_flair(flair_text="Material", flair_css_class="material")
        elif post.is_self is True:
            print("\tAssigning 'Discussion' flair")
            post.set_flair(flair_text="Discussion",
                           flair_css_class="discussion")
        elif any(word in ptitle for word in HWSTRING):
            print("\tAssigning 'Hardware' flair")
            post.set_flair(flair_text="Hardware",
                           flair_css_class="hardware")
        elif any(word in purl for word in EXTENSIONS):
            print("\tAssigning 'Workflow' flair")
            post.set_flair(flair_text="Workflow",
                           flair_css_class="workflow")
        else:
            print("\tAssigning 'Screenshot' flair")
            post.set_flair(flair_text="Screenshot",
                           flair_css_class="screenshot")
        print("\tFlair Assigned")
    else:
        print("\tAlready Flaired")


def approve_host(post, purl, ptitle):
    print("Verifying hosts...")
    if any(domain in purl for domain in WHITELIST) or post.is_self:
        pass
    elif "[oc]" in ptitle:
        # Materials can come from any website
        pass
    else:
        slay(post, HOSTRESPONSE)


def details_scan(post, pauthor, ptime):
    """
    Function which check if a post contains a details comment and then takes
    the appropriate action. Also returns True if done with post and returns
    False if future action on the post will be needed.
    """

    comments = helpers.flatten_tree(post.comments)
    commenters = []
    for comment in comments:
        try:
            commenters.append(comment.author.name)
        except AttributeError:
            commenters.append("[deleted]")

    if pauthor in commenters:
        print("\tComment is okay")
        # Deletes all the bot's comments
        for comment, cauthor in zip(comments, commenters):
            if cauthor == USERNAME:
                comment.delete()
        print("\tDeleted old bot comments")
        return True

    else:
        curtime = datetime.now(timezone.utc).timestamp()
        difference = curtime - ptime

        if difference > DELAY:
            slay(post, NODETAILS)
            return True

        elif difference > (DELAY * 0.5):
            commenters = [comment.author.name for comment in comments]
            print("\tWarning OP")
            response = post.add_comment(DETAILSWARN)
            response.distinguish()
            return False

        else:
            if difference < (DELAY * 0.5):
                differences = str("%.0f" % ((DELAY * 0.5) - difference))
                print("\tStill has " + differences + "s before warning")
            elif difference < DELAY:
                differences = str("%.0f" % (DELAY - difference))
                print("\tStill has " + differences + "s before removal")
            return False


def actions(post):
    # Post variables
    pid = post.id
    ptitle = post.title.lower()
    purl = post.url
    ptime = post.created_utc
    try:
        pauthor = post.author.name
    except AttributeError:
        pauthor = "[DELETED]"
    try:
        flair = post.link_flair_text.lower()
    except AttributeError:
            flair = ""
    # Post actions
    print("\nScanning " + pid + " by " + pauthor)
    flair_assign(post, purl, ptitle, flair)
    if details_scan(post, pauthor, ptime):
        with open("oldposts", "a+") as file:
            file.write(pid + "\n")
    tag_check(post, ptitle)
    approve_host(post, purl, ptitle)


"""RUNNING BOT"""

print("Running on /r/" + SUBREDDIT)
while True:
    print("\nRunning at " + str(datetime.now(timezone.utc)))
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_new(limit=MAXPOSTS)
    try:
        with open("oldposts", "r") as file:
            oldposts = [line.strip() for line in file]
    except:
        oldposts = []
    try:
        for post in posts:
            if post.id in oldposts:
                pass
            else:
                actions(post)
    except Exception as e:
        print("An error has occurred\n", e)
    for var in range(WAIT, 0, -1):
        stdout.write("\rRunning again in " + str(var) + "s. ")
        stdout.flush()
        sleep(1)
    stdout.write("\r" + " "*28)
    stdout.flush()
