#!/usr/bin/python3

# This is a modification and merge of several reddit bots
# written by /u/GoldenSights for various subs. This is an
# AutoMod bot which scans /r/unixporn for new posts while
# making sure that the rules are being followed. All work
# is licensed under the MIT License, without any warranty

# Required modules
import datetime
import praw
import sqlite3
import sys
import time



"""CONFIGURATION"""

# Bot's Username
USERNAME  = "USER_HERE"
# Bot's Password
PASSWORD  = "PASS_HERE"
# Short description of what the bot does
USERAGENT = "Automated moderator for /r/unixporn (currently in testing)"
# Sub to scan for new posts
SUBREDDIT = "thewastelands"

# How many posts to retrieve at once (max 100)
MAXPOSTS = 10
# How many seconds to wait inbetween cycles. Bot is inactive during this time.
WAIT = 60
# Mods aren"t excempt
IGNOREMODS = False
# Time before post is removed
DELAY = 600
# Minimum comment lentgh
MINLENGTH = 10

# Hardware tags
HWSTRING = ["[desktop]", "[laptop]", "[server]", "[phone]", "[tablet]", "[multi]"]
# Tags to look for in post titles
TAGSTRING = ["[question]", "[discussion]", "[oc]", "[material]", "[meta]"]
# Tags to look for
OSSTRING = ["[arch]", "[archlinux]", "[arch linux]", "[ubuntu]", "[debian]", "[crunchbang]", "[#!]", "[fedora]", "[mint]", "[linux mint]", "[linuxmint]", "[eos]", "[elementary]", "[elementaryos]", "[elementary os]", "[manjaro]", "[gentoo]", "[opensuse]", "[slackware]", "[crux]", "[funtoo]", "[exherbo]", "[lmde]", "[lubuntu]", "[bodhi]", "[centos]", "[nixos]", "[korora]", "[parabola]", "[chakra]", "[lfs]", "[xubuntu]", "[kubuntu]", "[linux]", "[gnu/linux]", "[android]", "[bsd]", "[aix]", "[plan9]", "[freebsd]", "[openbsd]", "[dragonflybsd]", "[netbsd]"] 
# Whitelisted websites
WHITELIST = ["self."+SUBREDDIT, "imgur.com", "minus.com", "gfycat.com", "pub.iotek.org", "u.teknik.io", "mediacru.sh"]

# Message about reporting errors
CONTACT = "\n\n*^[Contact](http://www.reddit.com/message/compose?to=%2Fr%2F{0}) ^[us](http://www.reddit.com/message/compose?to=%2Fr%2F{0}) ^(if our bot has messed up)*".format(SUBREDDIT)
# Link to details template
TEMPLATE = "[details comment](http://www.reddit.com/r/{0}/wiki/info/template)".format(SUBREDDIT)

# Remobal message
MESSAGE = "You have not provided a {0} so the post has been removed. Please add one and message the mod team so we can approve your post.{1}".format(TEMPLATE, CONTACT)
# Message when minimum length not met
TOOSHORT = "You have added a {0}, but it looks quite short. Try to add some more info.{1}".format(TEMPLATE, CONTACT)
# Bots message for use of lack of tags
NOTAGREPLYSTRING = "Your post title appears to be missing a [tag]. See [section 3](http://www.reddit.com/r/unixporn/wiki/info/rules#wiki_3.0_-_categorisation) for more details but briefly:\n\n* Screenshots requires [WM/DE]\n\n* Workflow requires [WM/DE]\n\n* Hardware requires [DEVICE]{0}".format(CONTACT)
# Bots message for use of deprecated tags
TAGREPLYSTRING = "Your post appeats to be using one of the deprecated [tags]. Please use a link flair instead.{0}".format(CONTACT)
# Bots reply
OSREPLYSTRING = "Your post appeats to be using the OS [tag]. This is now deprecated in favour of userflair.{0}".format(CONTACT)
# Bots message for non approved hosts
HOSTRESPONSE = "You don't appear to be using an [approved host](http://www.reddit.com/r/unixporn/wiki/info/rules#wiki_2.0_-_hosting). Please resubmit using one of them, but feel free to leave mirrors to host in your details comment.{0}".format(CONTACT)

print(SUBREDDIT, "bot\n")


"""DATABASE LOADING"""

# weekly_post_db = sqlite3.connect("weekly_post.db")
# print("Loaded weekly-post database")
# weekly_post_cur = weekly_post_db.cursor()
# weekly_post_cur.execute("CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)")
# print("Loaded weekly-post table")
# weekly_post_db.commit()

tag_check_db = sqlite3.connect("tag_check.db")
print("Loaded tag-check database")
tag_check_cur = tag_check_db.cursor()
tag_check_cur.execute("CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)")
print("Loaded tag-check table")
tag_check_db.commit()

os_check_db = sqlite3.connect("os_check.db")
print("Loaded OS-check database")
os_check_cur = os_check_db.cursor()
os_check_cur.execute("CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)")
print("Loaded OS-check table")
os_check_db.commit()

approve_host_db = sqlite3.connect("approve_host.db")
print("Loaded approved-host database")
approve_host_cur = approve_host_db.cursor()
approve_host_cur.execute("CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)")
print("Loaded approved-host table")
approve_host_db.commit()

flair_assign_db = sqlite3.connect("flair_assign.db")
print("Loaded flair-assign database")
flair_assign_cur = flair_assign_db.cursor()
flair_assign_cur.execute("CREATE TABLE IF NOT EXISTS oldposts(id TEXT)")
print("Loaded Oldposts")
flair_assign_db.commit()

details_scan_db = sqlite3.connect("details_scan.db")
print("Loaded details-scan database")
details_scan_cur = details_scan_db.cursor()
details_scan_cur.execute("CREATE TABLE IF NOT EXISTS oldposts(id TEXT)")
print("Loaded flair-assign table")
details_scan_db.commit()



"""BOT LOGIN"""

r = praw.Reddit(USERAGENT)
Trying = True
while Trying:
	try:
		r.login(USERNAME, PASSWORD)
		print("\nSuccessfully logged in\n")
		Trying = False
	except praw.errors.InvalidUserPass:
		print("Wrong Username or Password")
		quit()
	except Exception as e:
		print("%s" % e)
		time.sleep(5)



"""DEFINING FUNCTIONS"""

def getTime(bool):
	timeNow = datetime.datetime.now(datetime.timezone.utc)
	timeUnix = timeNow.timestamp()
	if bool == False:
		return timeNow
	else:
		return timeUnix



"""DEFINING BOT ACTIONS"""

def weekly_post():
	# Not finished
	# print("Checking weekend post...")
	pass


def tag_check():
	print("Scanning for title tags...")
	subreddit = r.get_subreddit(SUBREDDIT)
	posts = subreddit.get_new(limit=MAXPOSTS)
	for post in posts:
		pid = post.id
		try:
			pauthor = post.author.name
		except AttributeError:
			pauthor = "[DELETED]"
		tag_check_cur.execute("SELECT * FROM oldposts WHERE ID=?", [pid])
		if not tag_check_cur.fetchone():
			tag_check_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])
			pbody = post.selftext.lower()
			pbody += " " + post.title.lower()

			if any(key.lower() in pbody for key in TAGSTRING):
				print("Replying to " + pid + " by " + pauthor)
				response = post.add_comment(TAGREPLYSTRING)
				response.distinguish()
				post.remove(spam=False)
				print("\tPost removed")
				time.sleep(5)

			if any(tag in pbody for tag in ["[", "]"]):
				print("Replying to " + pid + " by " + pauthor)
				response = post.add_comment(NOTAGREPLYSTRING)
				response.distinguish()
				post.remove(spam=False)
				print("\tPost removed")
				time.sleep(5)
	
	tag_check_db.commit()


def os_check():
	print("Scanning for OS tags...")
	subreddit = r.get_subreddit(SUBREDDIT)
	posts = subreddit.get_new(limit=MAXPOSTS)
	for post in posts:
		pid = post.id
		try:
			pauthor = post.author.name
		except AttributeError:
			pauthor = "[DELETED]"
		os_check_cur.execute("SELECT * FROM oldposts WHERE ID=?", [pid])
		if not os_check_cur.fetchone():
			os_check_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])
			pbody = post.selftext.lower()
			pbody += " " + post.title.lower()
			if any(key.lower() in pbody for key in OSSTRING):
				print("Replying to " + pid + " by " + pauthor)
				response = post.add_comment(OSREPLYSTRING)
				response.distinguish()
				post.remove(spam=False)
				print("\tPost removed")
				time.sleep(5)

	os_check_db.commit()


def approve_host():
	print("Scanning for non-approved hosts...")
	subreddit = r.get_subreddit(SUBREDDIT)
	posts = subreddit.get_new(limit=MAXPOSTS)
	for post in posts:
		pid = post.id
		try:
			pauthor = post.author.name
		except AttributeError:
			pauthor = "[DELETED]"
		approve_host_cur.execute("SELECT * FROM oldposts WHERE ID=?", [pid])
		if not approve_host_cur.fetchone():
			approve_host_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])
			pbody = post.url
			if any(domain in pbody for domain in WHITELIST):
				pass
			else:
				print("Replying to " + pid + " by " + pauthor)
				response = post.add_comment(HOSTRESPONSE)
				response.distinguish()
				post.remove(spam=False)
				print("\tPost removed")
				time.sleep(5)

	approve_host_db.commit()


def flair_assign():
	print("Scanning " + SUBREDDIT)
	subreddit = r.get_subreddit(SUBREDDIT)
	moderators = subreddit.get_moderators()
	mods = []
	for moderator in moderators:
		mods.append(moderator.name)
	posts = subreddit.get_new(limit=MAXPOSTS)
	for post in posts:
		pid = post.id
		ptitle = post.title.lower()
		purl = post.url
		try:
			pauthor = post.author.name
		except AttributeError:
			pauthor = "[deleted]"
		flair_assign_cur.execute("SELECT * FROM oldposts WHERE id=?", [pid])
		if not flair_assign_cur.fetchone():
			try:
				flair = post.link_flair_text.lower()
			except AttributeError:
				flair = ""

			if flair == "":
				print(pid + ": No Flair")

				if "self."+SUBREDDIT in purl:
					print("\tAssigning 'Discussion' flair")
					post.set_flair(flair_text=Discussion,flair_css_class=discussion)
					flair = "Discussion"
				
				elif any(word in ptitle for word in HWSTRING):
					print("\tAssigning 'Hardware' flair")
					post.set_flair(flair_text=Hardware,flair_css_class=hardware)
					flair = "Hardware"
				
				elif any(word in purl for word in [".webm", ".gif", "gfycat"]):
					print("\tAssigning 'Workflow' flair")
					post.set_flair(flair_text=Workflow,flair_css_class=workflow)
					flair = "Workflow"
				
				else:
					print("\tAssigning 'Screenshot' flair")
					post.set_flair(flair_text=Screenshot,flair_css_class=screenshot)
					flair = "Screenshot"
				
				print(pid + ", " + pauthor + ": Flair Assigned")
			else:
				print(pid + ", " + pauthor + ": Already Flaired")
				flair_assign_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])

		flair_assign_db.commit()


def details_scan():
	print("Scanning for details comments...")
	subreddit = r.get_subreddit(SUBREDDIT)
	moderators = subreddit.get_moderators()
	mods = []
	for moderator in moderators:
		mods.append(moderator.name)
	posts = subreddit.get_new(limit=MAXPOSTS)
	for post in posts:
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
		
		details_scan_cur.execute("SELECT * FROM oldposts WHERE id=?", [pid])
		if not details_scan_cur.fetchone():
			if post.is_self == False:
				if pauthor not in mods or IGNOREMODS == False:
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
							time.sleep(5)
							
						if found == True and short == True:
							print("\tFound comment, but reporting for length")
							post.report()
							response = post.add_comment(TOOSHORT)
							response.distinguish()
						
						if found == True and short == False:
							print("\tComment is okay. Passing")

						details_scan_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])
					else:
						differences = str("%.0f" % (DELAY - difference))
						print("\tStill has " + differences + "s.")
				
				if pauthor in mods and IGNOREMODS == True:
					print(pid + ", " + pauthor + ": Ignoring Moderator")
					details_scan_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])

			if post.is_self == True:
				print(pid + ", " + pauthor + ": Ignoring Selfpost")
				details_scan_cur.execute("INSERT INTO oldposts VALUES(?)", [pid])

		details_scan_db.commit()



"""RUNNING BOT"""

task_list = [
	weekly_post,
	tag_check,
	os_check,
	approve_host,
	flair_assign,
	details_scan
	]

print("Running on /r/{0}".format(SUBREDDIT))
while True:
	print("\nRunning at " + str(getTime(0)))
	try:
		for task in task_list:
			task()
	except Exception as e:
		print("An error has occured while running {0}\n".format(task), e)
	tag_check_db.commit()
	os_check_db.commit()
	approve_host_db.commit()
	flair_assign_db.commit()
	for var in range(WAIT, 0, -1):
		sys.stdout.write("\rRunning again in " + str(var) + " seconds ")
		sys.stdout.flush()
		time.sleep(1)
	sys.stdout.write("\r							")
	sys.stdout.flush()