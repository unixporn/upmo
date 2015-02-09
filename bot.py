#!/usr/bin/python3

# This is a modification and merge of several reddit bots
# written by /u/GoldenSights for various subs. This is an
# AutoMod bot which scans /r/unixporn for new posts while
# making sure that the rules are being followed. All work
# is licensed under the MIT License, without any warranty

# Required modules
from sys import stdout
from time import sleep
from datetime import datetime, timezone
from praw import errors, helpers, Reddit


"""CONFIGURATION"""

# Bot's Username
USERNAME = "USERNAME"
# Bot's Password
PASSWORD = "PASSWORD"
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
# WGW start
WGWNUMBER = 11
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

# Website Whitelist
WHITELIST = ["imgur.com",
             "minus.com",
             "gfycat.com",
             "pub.iotek.org",
             "u.teknik.io",
             "mediacru.sh"]

# Workflow extensions
EXTENSIONS = [".webm", ".gif", "gfycat", ".mp4"]

# Strings for the "Hardware" flair
HWSTRING = ["[desktop]",
            "[laptop]",
            "[server]",
            "[phone]",
            "[tablet]",
            "[portable]",
            "[multi]"]

# Title tags which shouldn't be used
TAGSTRING = ["[discussion]",
             "[help]",
             "[material]",
             "[meta]",
             "[question]",
             "[screenshot]",
             "[workflow]",
             "[hardware]",
             "[other]"]

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
            "debian",
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
            "xubuntu"]
OSSTRING = ["[" + OS + "]" for OS in OSSTRING]

# Message about reporting bot errors
CONTACT = "\n\n*^[Contact]({0}) ^[us]({0}) ^if ^our ^bot ^has ^messed " \
          "^up*".format(MODMSG)

# Message when haven't added a details comment
NODETAILS = "You have not provided a {0} so the post has been removed. " \
            "Please add one and message the mod team so we can approve " \
            "your post.{1}".format(TEMPLATE, CONTACT)

# Message when not using a tag
NOTAGREPLY = "Your post title appears to be missing a [tag]. " \
             "See [section 3]({0}) for more details but briefly:" \
             "\n\n* Screenshots requires [WM/DE]\n\n* Workflow " \
             "requires [WM/DE]\n\n* Hardware requires [DEVICE]" \
             "\n\n* Material requires [OC]{1}".format(CATLINK, CONTACT)

# Message when using a deprecated tag
DEPTAGREPLY = "Your post appears to be using one of the deprecated " \
              "[tags]. Please use a link flair instead." + CONTACT

# Message when stating OS in a title tag
OSREPLY = "Your post appears to be using the OS [tag]. This is " \
          "now deprecated in favour of userflair." + CONTACT

# Message when not using an approved host
HOSTRESPONSE = "You don't appear to be using an [approved host]({0}). " \
               "Please resubmit using one of them, but feel free to " \
               "leave mirrors to host in your details comment.{1}"
HOSTRESPONSE = HOSTRESPONSE.format(HOSTLINK, CONTACT)

# Warning when haven't added a details comment
DETAILSWARN = "Please add a {0}.{1}".format(TEMPLATE, CONTACT)

# Post body for weekly thread
WGWBODY = "In this thread users can post any screenshot, no matter " \
          "how close to default it may be, and any question, no mater " \
          "how stupid they think it may be. For this discussion we will " \
          "be lax in enforcing 2.1-5, 2.7-9 and 3.1-2. This basically means " \
          "you can post anything on topic, in any format you like, and " \
          "using any host. We hope this gives new users a chance to get " \
          "some help with any problems they're having and older users a " \
          "chance to show of their knowledge by helping those in need." \
          "\n\nPlease respect that the lax rules for WGW apply only " \
          "within this thread and normal submission rules still apply " \
          "for the main sub." + CONTACT

# Message when user just comments '.'
USESAVEPM = "You seem to be using a '.' comment to save threads. This is " \
            "one of our most reported comment types and so has been removed." \
            " Please use a bookmarking tool instead." + CONTACT

print(SUBREDDIT, "bot\n")


"""BOT LOGIN"""

r = Reddit(USERAGENT)
Trying = True
while Trying:
    try:
        r.login(USERNAME, PASSWORD)
        print("Successfully logged in\n")
        Trying = False
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


def weekly_post(WGWNUMBER):
    now = datetime.now()
    if now.weekday() == 5 and now.hour == 0 and now.minute == 0:
        print("Creating weekend post...")
        title = "\"Whatever Goes\" weekend #" + WGWNUMBER
        newpost = r.submit(SUBREDDIT, title, text=WGWBODY, captcha=None)
        newpost.distinguish()
        WGWNUMBER += 1


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
    if any(domain in purl for domain in WHITELIST) or post.is_self is True:
        pass
    else:
        # Materials currently exempt
        if "[oc]" in ptitle:
            pass
        else:
            slay(post, HOSTRESPONSE)


def details_scan(post, pauthor, ptime):
    found = False
    curtime = datetime.now(timezone.utc).timestamp()
    if post.is_self is False:
        print("Checking details comments...")
        difference = curtime - ptime
        comments = helpers.flatten_tree(post.comments)
        for comment in comments:
            try:
                cauthor = comment.author.name
            except AttributeError:
                cauthor = "[deleted]"
            if cauthor == pauthor and found is False:
                print("\tFound comment by OP")
                found = True
        if found is True:
            print("\tComment is okay. Passing")
        else:
            if difference > DELAY:
                slay(post, NODETAILS)
            elif difference > (DELAY * 0.5):
                commenters = [comment.author.name for comment in comments]
                if (found is False) and ("upmo" not in commenters):
                    print("\tWarning OP")
                    response = post.add_comment(DETAILSWARN)
                    response.distinguish()
                return False
            else:
                differences = str("%.0f" % (DELAY - difference))
                print("\tStill has " + differences + "s.")
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
    tag_check(post, ptitle)
    flair_assign(post, purl, ptitle, flair)
    approve_host(post, purl, ptitle)
    if details_scan(post, pauthor, ptime) is False:
        pass
    else:
        with open("oldposts", "a+") as file:
            file.write(pid + "\n")


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
        weekly_post(WGWNUMBER)
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
