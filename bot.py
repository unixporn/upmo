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
USERNAME  = "USERNAME"
# Bot's Password
PASSWORD  = "PASSWORD"
# Sub to scan for new posts
SUBREDDIT = "SUBREDDIT"
# Short description of what the bot does
USERAGENT = "Automated moderator for /r/" + SUBREDDIT

# How many posts to retrieve at once (max 100)
MAXPOSTS = 10
# How many seconds to wait inbetween cycles. Bot is inactive during this time.
WAIT = 60
# Time before post is removed
DELAY = 1200
# WGW start
WGWNUMBER = 8

# Direct link to send mod mail
MODMSG = "http://www.reddit.com/message/compose?to=%2Fr%2F" + SUBREDDIT
# Direct link for information about hosting
HOSTLINK = "http://www.reddit.com/r/" + SUBREDDIT + "/wiki/info/rules#wiki_2.0_-_hosting"
# Direct link for information about post catagories
CATLINK = "http://www.reddit.com/r/" + SUBREDDIT + "/wiki/info/rules#wiki_3.0_-_categorisation"
# Markdown formatted link for details comment template
TEMPLATE = "[details comment](http://www.reddit.com/r/" + SUBREDDIT + "/wiki/info/template)"

# Website Whitelist
WHITELIST = ["imgur.com", "minus.com", "gfycat.com", "pub.iotek.org", "u.teknik.io", "mediacru.sh"]
# Strings for the "Hardware" flair
HWSTRING = ["[desktop]", "[laptop]", "[server]", "[phone]", "[tablet]", "[multi]"]
# Title tags which shouldn't be used
TAGSTRING = ["[discussion]", "[help]", "[material]", "[meta]", "[oc]"]
# Banned OS title tags
OSSTRING = ["aix",
			"android",
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
			"ubuntu",
			"xubuntu"]
OSSTRING = ["[" + OS + "]" for OS in OSSTRING]

# Message about reporting bot errors
CONTACT = "\n\n*^[Contact]({0}) ^[us]({0}) ^if ^our ^bot ^has ^messed ^up)*".format(MODMSG)

# Message when haven't added a details comment
NODETAILS = "You have not provided a {0} so the post has been removed." \
			"Please add one and message the mod team so we can approve " \
			"your post.{1}".format(TEMPLATE, CONTACT)

# Message when not using a tag
NOTAGREPLY = "Your post title appears to be missing a [tag]. " \
			 "See [section 3]({0}) for more details but briefly:" \
			 "\n\n* Screenshots requires [WM/DE]\n\n* Workflow " \
			 "requires [WM/DE]\n\n* Hardware requires [DEVICE]" \
			 "\n\n* Material requires [TYPE]{1}".format(CATLINK, CONTACT)

# Message when using a deprecated tag
DEPTAGREPLY = "Your post appeats to be using one of the deprecated " \
			  "[tags]. Please use a link flair instead." + CONTACT

# Message when stating OS in a title tag
OSREPLY = "Your post appeats to be using the OS [tag]. This is " \
		  "now deprecated in favour of userflair." + CONTACT

# Message when not using an approved host
HOSTRESPONSE = "You don't appear to be using an [approved host](). " \
			   "Please resubmit using one of them, but feel free to " \
			   "leave mirrors to host in your details comment." + CONTACT

# Warning when haven't added a details comment
DETAILSWARN = "Please add a {0}.{1}".format(TEMPLATE, CONTACT)

# Post body for weekly thread
WGWBODY = "In this thread users can post any screenshot, no matter " \
		  "how close to default it may be, and any question, no mater " \
		  "how stupid they think it may be. For this discussion rules " \
		  "2.1-5, 2.7-9 and 3.1-2 are all laxed. This basically means " \
		  "you can post anything on topic, in any format you like, and " \
		  "using any host. We hope this gives new users a chance to get " \
		  "some help with any problems they're having and older users a " \
		  "chance to show of their knowledge by helping those in need." \
		  "\n\nPlease respect that the lax rules for WGW apply only " \
		  "within this thread and normal submission rules still apply " \
		  "for the main sub." + CONTACT

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


def weekly_post():
	now = datetime.now()
	if now.weekday() == 5 and now.hour == 0 and now.minute == 0:
		print("Creating weekend post...")
		newpost = r.submit(SUBREDDIT, "\"Whatever Goes\" weekend #{0}".format(WGWNUMBER), text=WGWBODY)
		newpost.distinguish()
		WGWNUMBER += 1


def tag_check(post, pid, pauthor, ptitle):
	print("Checking tags...")

	if any(key.lower() in ptitle for key in TAGSTRING):
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(DEPTAGREPLY)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)

	elif any(key.lower() in ptitle for key in OSSTRING):
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(OSREPLY)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)

	elif any(tag in ptitle for tag in ["[", "]"]) or post.is_self == True:
		pass
	else:
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(NOTAGREPLY)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)


def approve_host(post, pid, pauthor, purl):
	print("Verifying hosts...")

	if any(domain in purl for domain in WHITELIST) or post.is_self == True:
		pass
	else:
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(HOSTRESPONSE)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)


def flair_assign(post, pid, pauthor, purl, ptitle, flair):
	print("Scanning for flairs...")

	if flair == "":
		print(pid + ": No Flair")

		if post.is_self == True:
			print("\tAssigning 'Discussion' flair")
			post.set_flair(flair_text="Discussion",flair_css_class="discussion")
			
		elif any(word in ptitle for word in HWSTRING):
			print("\tAssigning 'Hardware' flair")
			post.set_flair(flair_text="Hardware",flair_css_class="hardware")
			
		elif any(word in purl for word in [".webm", ".gif", "gfycat", ".mp4"]):
			print("\tAssigning 'Workflow' flair")
			post.set_flair(flair_text="Workflow",flair_css_class="workflow")
			
		else:
			print("\tAssigning 'Screenshot' flair")
			post.set_flair(flair_text="Screenshot",flair_css_class="screenshot")
				
		print(pid + ", " + pauthor + ": Flair Assigned")
	else:
		print(pid + ", " + pauthor + ": Already Flaired")


def details_scan(post, pid, pauthor, ptime):
	print("Checking details comments...")
	found = False
	curtime = datetime.now(timezone.utc).timestamp()

	if post.is_self == False:
		difference = curtime - ptime
				
		print(pid + ", " + pauthor + ": Finding comments")
		comments = helpers.flatten_tree(post.comments)
		for comment in comments:
			cid = "t3_" + comment.id
			try:
				cauthor = comment.author.name
			except AttributeError:
				cauthor = "[deleted]"
			if cauthor == pauthor and found == False:
				print("\tFound comment by OP")
				found = True
		
		if found == True:
			print("\tComment is okay. Passing")

		else:
			if difference > DELAY:
				print("\tComments were empty, or OP was not found. Post will be removed.")
				response = post.add_comment(NODETAILS)
				response.distinguish()
				post.remove(spam=False)
				print("\tPost removed")
				sleep(5)
		
			elif difference > ( DELAY * 0.5 ):
				commenters = [comment.author.name for comment in comments]
				if (found == False) and ("upmo" not in commenters):
					print("Warning OP")
					response = post.add_comment(DETAILSWARN)
					response.distinguish()
				return False
		
			else:
				differences = str("%.0f" % (DELAY - difference))
				print("\tStill has " + differences + "s.")
				return False

	else:
		print(pid + ", " + pauthor + ": Ignoring Selfpost")


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
	print("\nScanning", pid)
	tag_check(post, pid, pauthor, ptitle)
	approve_host(post, pid, pauthor, purl)
	flair_assign(post, pid, pauthor, purl, ptitle, flair)
	if details_scan(post, pid, pauthor, ptime) == False:
		pass
	else:
		with open("oldposts","a+") as file:
			file.write(pid + "\n")



"""RUNNING BOT"""

print("Running on /r/{0}".format(SUBREDDIT))
while True:
	print("\nRunning at " + str(datetime.now(timezone.utc)))
	subreddit = r.get_subreddit(SUBREDDIT)
	posts = subreddit.get_new(limit=MAXPOSTS)
	with open("oldposts", "r") as file:
		oldposts = [line.strip() for line in file]
	try:
		weekly_post()
		for post in posts:
			if post.id in oldposts:
				pass
			else:
				actions(post)
	except Exception as e:
		print("An error has occured\n", e)

	for var in range(WAIT, 0, -1):
		stdout.write("\rRunning again in " + str(var) + "s. ")
		stdout.flush()
		sleep(1)
	stdout.write("\r" + " "*28)
	stdout.flush()
