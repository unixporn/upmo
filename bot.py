#!/usr/bin/python3

# This is a modification and merge of several reddit bots
# written by /u/GoldenSights for various subs. This is an
# AutoMod bot which scans /r/unixporn for new posts while
# making sure that the rules are being followed. All work
# is licensed under the MIT License, without any warranty

# Required modules
import datetime
import praw
from sys import stdout
from time import sleep



"""CONFIGURATION"""

# Bot's Username
USERNAME  = "USERNAME"
# Bot's Password
PASSWORD  = "PASSWORD"
# Sub to scan for new posts
SUBREDDIT = "SUBREDDIT"
# Short description of what the bot does
USERAGENT = "Automated moderator for /r/{0} (currently in testing)".format(SUBREDDIT)

# How many posts to retrieve at once (max 100)
MAXPOSTS = 10
# How many seconds to wait inbetween cycles. Bot is inactive during this time.
WAIT = 60
# Mods aren"t excemptoldposts
IGNOREMODS = False
# Time before post is removed
DELAY = 1200
# Minimum comment lentgh
MINLENGTH = 10
# WGW start
WGWNUMBER = 8

# Hardware tags
HWSTRING = ["[desktop]", "[laptop]", "[server]", "[phone]", "[tablet]", "[multi]"]
# Deprecated tags
TAGSTRING = ["[question]", "[discussion]", "[oc]", "[material]", "[meta]"]
# OS tags
OSSTRING = ["[arch]", "[archlinux]", "[arch linux]", "[ubuntu]", "[debian]", "[crunchbang]", "[#!]", "[fedora]", "[mint]", "[linux mint]", "[linuxmint]", "[eos]", "[elementary]", "[elementaryos]", "[elementary os]", "[manjaro]", "[gentoo]", "[opensuse]", "[slackware]", "[crux]", "[funtoo]", "[exherbo]", "[lmde]", "[lubuntu]", "[bodhi]", "[centos]", "[nixos]", "[korora]", "[parabola]", "[chakra]", "[lfs]", "[xubuntu]", "[kubuntu]", "[linux]", "[gnu/linux]", "[android]", "[bsd]", "[aix]", "[plan9]", "[freebsd]", "[openbsd]", "[dragonflybsd]", "[netbsd]"] 
# Whitelisted websites
WHITELIST = ["imgur.com", "minus.com", "gfycat.com", "pub.iotek.org", "u.teknik.io", "mediacru.sh"]

# Message about reporting errors
CONTACT = "\n\n*^[Contact](http://www.reddit.com/message/compose?to=%2Fr%2F{0}) ^[us](http://www.reddit.com/message/compose?to=%2Fr%2F{0}) ^(if our bot has messed up)*".format(SUBREDDIT)
# Link to details template
TEMPLATE = "[details comment](http://www.reddit.com/r/{0}/wiki/info/template)".format(SUBREDDIT)

# Lack of details
MESSAGE = "You have not provided a {0} so the post has been removed. Please add one and message the mod team so we can approve your post.{1}".format(TEMPLATE, CONTACT)
# Short details
TOOSHORT = "You have added a {0}, but it looks quite short. Try to add some more info.{1}".format(TEMPLATE, CONTACT)
# Missing tags
NOTAGREPLYSTRING = "Your post title appears to be missing a [tag]. See [section 3](http://www.reddit.com/r/unixporn/wiki/info/rules#wiki_3.0_-_categorisation) for more details but briefly:\n\n* Screenshots requires [WM/DE]\n\n* Workflow requires [WM/DE]\n\n* Hardware requires [DEVICE]{0}".format(CONTACT)
# Deprecated tags
TAGREPLYSTRING = "Your post appeats to be using one of the deprecated [tags]. Please use a link flair instead.{0}".format(CONTACT)
# OS Tag
OSREPLYSTRING = "Your post appeats to be using the OS [tag]. This is now deprecated in favour of userflair.{0}".format(CONTACT)
# Approved host
HOSTRESPONSE = "You don't appear to be using an [approved host](http://www.reddit.com/r/unixporn/wiki/info/rules#wiki_2.0_-_hosting). Please resubmit using one of them, but feel free to leave mirrors to host in your details comment.{0}".format(CONTACT)
# Details warning
DETAILSSTRING = "Please add a {0}.{1}".format(TEMPLATE, CONTACT)
# WGW body
WGWBODY = "In this thread users can post any screenshot, no matter how close to default it may be, and any question, no mater how stupid they think it may be. For this discussion rules 2.1-5, 2.7-9 and 3.1-2 are all laxed. This basically means you can post anything on topic, in any format you like, and using any host. We hope this gives new users a chance to get some help with any problems they're having and older users a chance to show of their knowledge by helping those in need.\n\nPlease respect that the lax rules for WGW apply only within this thread and normal submission rules still apply for the main sub."


print(SUBREDDIT, "bot\n")



"""BOT LOGIN"""

r = praw.Reddit(USERAGENT)
Trying = True
while Trying:
	try:
		r.login(USERNAME, PASSWORD)
		print("Successfully logged in\n")
		Trying = False
	except praw.errors.InvalidUserPass:
		print("Wrong Username or Password\n")
		quit()
	except Exception as e:
		print("%s" % e)
		sleep(5)



"""DEFINING FUNCTIONS"""

def getTime(bool):
	timeNow = datetime.datetime.now(datetime.timezone.utc)
	timeUnix = timeNow.timestamp()
	if bool == False:
		return timeNow
	else:
		return timeUnix


def weekly_post():
	now = datetime.datetime.now()
	if now.weekday() == 5 and now.hour == 0 and now.minute == 0:
		print("Creating weekend post...")
		newpost = r.submit(SUBREDDIT, "\"Whatever Goes\" weekend #{0}".format(WGWNUMBER), text=WGWBODY)
		newpost.distinguish()
		WGWNUMBER += 1


def tag_check(post):
	print("Checking tags...")
	pid = post.id
	try:
		pauthor = post.author.name
	except AttributeError:
		pauthor = "[DELETED]"
	ptitle = post.title.lower()

	if any(key.lower() in ptitle for key in TAGSTRING):
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(TAGREPLYSTRING)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)

	if any(key.lower() in ptitle for key in OSSTRING):
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(OSREPLYSTRING)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)

	if any(tag in ptitle for tag in ["[", "]"]) or post.is_self == True:
		pass
	else:
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(NOTAGREPLYSTRING)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)


def approve_host(post):
	print("Verifying hosts...")
	pid = post.id
	try:
		pauthor = post.author.name
	except AttributeError:
		pauthor = "[DELETED]"
	pbody = post.url
	if any(domain in pbody for domain in WHITELIST) or post.is_self == True:
		pass
	else:
		print("Replying to " + pid + " by " + pauthor)
		response = post.add_comment(HOSTRESPONSE)
		response.distinguish()
		post.remove(spam=False)
		print("\tPost removed")
		sleep(5)


def flair_assign(post):
	print("Scanning for flairs...")
	pid = post.id
	ptitle = post.title.lower()
	purl = post.url
	try:
		pauthor = post.author.name
	except AttributeError:
		pauthor = "[deleted]"
	try:
		flair = post.link_flair_text.lower()
	except AttributeError:
			flair = ""

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


def details_scan():
	print("Checking details comments...")
	found = False
	short = False
	opc = []
	pid = post.id
	try:
		pauthor = post.author.name
	except AttributeError:
		pauthor = "[deleted]"
	ptime = post.created_utc
	curtime = getTime(True)		

	if post.is_self == False:
		difference = curtime - ptime
				
		print(pid + ", " + pauthor + ": Finding comments")
		comments = praw.helpers.flatten_tree(post.comments)
		for comment in comments:
			cid = "t3_" + comment.id
			try:
				cauthor = comment.author.name
			except AttributeError:
				cauthor = "[deleted]"
			if cauthor == pauthor and found == False:
				print("\tFound comment by OP")
				found = True
				cbody = comment.body
				clength = len(cbody)
				opc.append(clength)

		if found == True:
			if all(num < MINLENGTH for num in opc):
				print("\tAll OP comments too short")
				short = True
				
		if difference > DELAY:		 
			if found == False:
				print("\tComments were empty, or OP was not found. Post will be removed.")
				response = post.add_comment(MESSAGE)
				response.distinguish()
				post.remove(spam=False)
				print("\tPost removed")
				sleep(5)
							
			if found == True and short == True:
				print("\tFound comment, but reporting for length")
				post.report()
				response = post.add_comment(TOOSHORT)
				response.distinguish()
					
			if found == True and short == False:
				print("\tComment is okay. Passing")
		
		elif difference > ( DELAY * 0.5 ):
			commenters = [comment.author.name for comment in comments]
			if "upmo" not in commenters:
				print("Warning OP")
				response = post.add_comment(DETAILSSTRING)
				response.distinguish()
			return False
		
		else:
			differences = str("%.0f" % (DELAY - difference))
			print("\tStill has " + differences + "s.")
			return False

	if post.is_self == True:
		print(pid + ", " + pauthor + ": Ignoring Selfpost")



"""RUNNING BOT"""

print("Running on /r/{0}".format(SUBREDDIT))
while True:
	print("\nRunning at " + str(getTime(0)))
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
				print("\nScanning", post.id)
				tag_check(post)
				approve_host(post)
				flair_assign(post)
				if details_scan() == False:
					pass
				else:
					with open("oldposts","a+") as file:
						file.write(post.id + "\n")
	except Exception as e:
		print("An error has occured\n", e)
	for var in range(WAIT, 0, -1):
		stdout.write("\rRunning again in " + str(var) + "s. ")
		stdout.flush()
		sleep(1)
	stdout.write("\r" + " "*28)
	stdout.flush()
