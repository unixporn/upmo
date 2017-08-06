#!/usr/bin/python3

"""
This is an AutoMod bot which scans r/unixporn for new posts while making sure
that the rules are being followed. It's a modification & merge of several bots
written by u/GoldenSights for various subs. MIT Licensed, without any warranty
"""

# Required modules
from sys import stdout
from time import sleep, strftime, time
from getpass import getpass
from praw import errors, helpers, Reddit


# CONFIGURATION

# Bot's Username
USERNAME = "USERNAME"
# Sub to scan for new posts
SUBREDDIT = "SUBREDDIT"
# Short description of what the bot does
USERAGENT = "Automated moderator for r/" + SUBREDDIT

# How many posts to retrieve at once (max 100)
MAXPOSTS = 10
# Time before post is removed
DELAY = 1800
# Toggles whether bot reports before removal
TRUSTME = True

# Reddit URL
RURL = "https://www.reddit.com/"
# Link to a Reddit's rule page
RULELINK = RURL + "r/" + SUBREDDIT + "/about/rules"
# Direct link to send mod mail
MODMSG = RURL + "message/compose?to=%2Fr%2F" + SUBREDDIT
# Markdown formatted link for details comment template
TEMPLATE = "[details comment]({0}r/{1}/wiki/info/template)"
TEMPLATE = TEMPLATE.format(RURL, SUBREDDIT)

# Message about reporting bot errors
CONTACT = "\n\n*^[Contact]({0}) ^[us]({0}) ^if ^our ^bot ^has ^messed " \
          "^up*".format(MODMSG)

# Message when haven't added a details comment
NODETAILS = "You have not provided a {0} so the post has been removed. " \
            "Please add one and message the mod team so we can approve " \
            "your post.{1}".format(TEMPLATE, CONTACT)

# Message when not using a tag
NOTAGREPLY = "Your post appears to be missing a title [tag] so has " \
             "been removed. See [rule 4]({0}) for more details but " \
             "briefly:\n\n* Screenshots requires [WM/DE]\n\n* Workflow " \
             "requires [WM/DE]\n\n* Hardware requires [DEVICE]\n\n" \
             "* Material requires [OC]{1}".format(RULELINK, CONTACT)

# Message when using a deprecated tag
DEPTAGREPLY = "Your post appears to be using one of the deprecated " \
              "[tags] so has been removed. The bot will automatically " \
              "apply the relevant link flair to posts." + CONTACT

# Message when stating OS in a title tag
OSREPLY = "Your post appears to be using the OS [tag] so has been " \
          "removed. This is now deprecated in favour of userflair." + CONTACT

# Message when not using an approved host
HOSTRESPONSE = "You don't appear to be using an approved host: see " \
               "[rule 2]({0}) for more details. Please resubmit using " \
               "one of them, but feel free to leave mirrors to host " \
               "in your details comment.{1}".format(RULELINK, CONTACT)

# Message when people post with Teknik
TEKNIKPST = "https://redd.it/6ln5km"
TEKNIKMSG = "Teknik is one of our approved hosts but is currently " \
            "experiencing some [technical difficulties]({0}). While " \
            "this issue is being resolved plase repost using [another "\
            "host]({1}).{2}".format(TEKNIKPST, RULELINK, CONTACT)

# Warning when haven't added a details comment
DETAILSWARN = "Please add a {0}.{1}".format(TEMPLATE, CONTACT)


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
WHITELIST = [
    # Reddit
    "g.redditmedia.com",
    "i.redd.it",
    "i.reddituploads.com",
    "v.redd.it",
    # Imgur
    "imgur.com",
    # Gfycat
    "gfycat.com",
    # IOPaste
    "pub.iotek.org",
    # Teknik
    # "u.teknik.io",
    # "upload.teknik.io",
    # "v.teknik.io",
    # Other
    "redditmetrics.com/r/unixporn"
]

# Workflow extensions
EXTENSIONS = [".webm", ".gif", "gfycat", ".mp4", "v.redd.it"]

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
            "antergos",
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


# BOT LOGIN

print(SUBREDDIT, "bot\n")
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


# DEFINING FUNCTIONS

def slay(post, response):
    print("\tReplying to OP")
    res = post.add_comment(response)
    res.distinguish()
    if not TRUSTME:
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
    elif any(tag in ptitle for tag in ["[", "]"]) or post.is_self:
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
        elif post.is_self:
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
    elif "teknik.io" in purl:
        # Teknik currently having issues
        slay(post, TEKNIKMSG)
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

    print("Checking details comments...")
    comments = helpers.flatten_tree(post.comments)
    commenters = []
    for comment in comments:
        try:
            commenters.append(comment.author.name)
        except AttributeError:
            commenters.append("[deleted]")

    if post.is_self:
        print("\tSelf post so N/A")
        return True

    elif pauthor in commenters:
        print("\tComment is okay")
        # Deletes all the bot's comments
        for comment, cauthor in zip(comments, commenters):
            if cauthor == USERNAME:
                comment.delete()
        print("\tDeleted old bot comments")
        return True

    else:
        difference = time() - ptime

        if difference > DELAY:
            slay(post, NODETAILS)
            return True

        elif (difference > (DELAY * 0.5)) and ("upmo" not in commenters):
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


# RUNNING BOT

print("Running on r/" + SUBREDDIT)
while True:
    print("\nRunning at", strftime("%Y-%m-%d %H:%M:%S"))
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_new(limit=MAXPOSTS)
    try:
        with open("oldposts", "r") as file:
            oldposts = [line.strip() for line in file]
    except:
        oldposts = []
    for post in posts:
        if post.id in oldposts:
            pass
        else:
            actions(post)

    # Calculates seconds left in current minute
    secs = 60 - int(strftime("%S"))
    # Counts down until the next minute
    for var in range(secs, 0, -1):
        stdout.write("\rRunning again in %ss " % var)
        stdout.flush()
        sleep(1)
    stdout.write("\r" + " "*28 + "\n")
    stdout.flush()
