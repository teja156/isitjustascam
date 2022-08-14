#!/usr/bin/env python3
import sys
import os
import tldextract
import tweepy
import time
import os.path
import json
import re
import requests
from googleapiclient.discovery import build
import logging
import csv
import tldextract
from dotenv import load_dotenv
try:
	from .settings import BASE_DIR
except:
	from settings import BASE_DIR

import math
from datetime import datetime
sys.path.append(os.path.join(BASE_DIR))
from utils.checks import performChecks
from utils.dbconfig import dbconfig


load_dotenv()

CHECKS = ['WhoisCheck','GoogleCheck', 'DomainCheck_ServiceNames','DomainCheck_Hyphens','DomainCheck_TLDS','BadGrammarCheck','ContactPageCheck']
WAIT_TIME = 2 # minutes


logs_path = os.path.join(BASE_DIR,"logs")
if not os.path.exists(logs_path):
	os.mkdir(logs_path)

logging.basicConfig(
	handlers=[logging.FileHandler(filename=os.path.join(logs_path,'log.txt'), encoding='utf-8', mode='a+')],
	format='[%(asctime)s] [%(levelname)s]   %(message)s',
	level=logging.INFO,
	datefmt='%Y-%m-%d %H:%M:%S',
	force=True)

logger = logging.getLogger(__name__)

# creds_path = os.path.join(BASE_DIR,'creds','twittercreds.json')
# f=open(creds_path,"r")
# data = json.loads(f.read())
# f.close()
# BEARER_TOKEN = data['BEARER_TOKEN']
# API_KEY = data['API_KEY']
# API_KEY_SECRET = data['API_KEY_SECRET']
# ACCESS_TOKEN = data['ACCESS_TOKEN']
# ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
# USER_ID = data['USER_ID']
# BOT_USERNAME = data['BOT_USERNAME']

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
USER_ID = os.getenv("USER_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE")


client = tweepy.Client(bearer_token=BEARER_TOKEN, 
						consumer_key=API_KEY, 
						consumer_secret=API_KEY_SECRET, 
						access_token=ACCESS_TOKEN, 
						access_token_secret=ACCESS_TOKEN_SECRET, 
						return_type = dict,
						wait_on_rate_limit=True)



def resolveTwitterURL(url):
	try:
		r = requests.get(url, timeout=10)
		return r.url
	except Exception as e:
		logging.error("EXCEPTION OCCURED")
		logging.error("Couldn't resolve t.co to target URL")
		return None
	

def checkConnectivity(url):
	r = None
	try:
		r = requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, timeout=10)
	except Exception as e:
		logger.error("Could not connect to the URL")
		logger.error(str(e))
		return [False, "Connection Error"]
	
	if r.status_code!=200:
		return [False, f"Response code is {r.status_code} (not 200)"]
	
	return [True]

def postTweet(tweet_text,reply_to=""):
	logger.info(f"Posting tweet '{tweet_text}'")
	tweeted = None
	try:
		if reply_to=="":
			tweeted = client.create_tweet(text=tweet_text)
		else:
			tweeted = client.create_tweet(text=tweet_text, in_reply_to_tweet_id=reply_to)
		logger.info("Tweet posted")
		return tweeted['data']['id']
	except Exception as e:
		logger.error("Exception occured")
		logger.error(str(e))
		return None

def checkInDB(url):
	db = dbconfig()
	cursor = db.cursor()
	# query = f"SELECT * FROM twitterbot.scans WHERE target_url='{url}'"
	query = "SELECT * FROM twitterbot.scans WHERE target_url = %(url)s"
	cursor.execute(query,{'url':url})
	results = cursor.fetchall()

	# logger.info(f"checkInDB Retrieved results {str(results)}")

	if len(results)!=0:
		logger.info("Target URL already exists in scans db")
		return results[0][4] # return tweet id
	return None

def addToDB(tweet_id, tweet_author_username, tweet_author_id, url, results):
	# Add to DB
	logger.info("Adding scan results to DB")
	now = datetime.now()
	timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
	try:
		db = dbconfig()
		cursor = db.cursor()
		query = "INSERT INTO twitterbot.scans (timestamp,author_username,author_userid,target_url,tweet_id,scan_results) values (%s,%s,%s,%s,%s,%s)"
		val = (timestamp,tweet_author_username,tweet_author_id,url,tweet_id,str(results))
		cursor.execute(query,val)
		db.commit()
		db.close()
	except Exception as e:
		logger.error("Exception occured in addToDB")
		logger.error(str(e))

def checkWhitelist(url, test=False):
	path = os.path.join(BASE_DIR,"utils","top500Domains.csv")
	csvreader = []
	formatted_url = url.replace(".","[.]")
	with open(path, newline='') as f:
		reader = csv.reader(f)
		csvreader = list(reader)
		csvreader = csvreader[1:]
	for row in csvreader:
		d = row[1]
		extracted = tldextract.extract(d)
		famousdomain = {'name':extracted.domain, 'tld':extracted.suffix}
		extracted2 = tldextract.extract(url)
		domain = {'name':extracted2.domain, 'tld':extracted2.suffix}

		if famousdomain['name'] == domain['name'] and famousdomain['tld'] == domain['tld']:
			# Whitelisted
			if test:
				return {"status":"OK"}
			
			return True
	
	if test:
		return {"status":"NOK"}
	
	return False

def analyzeAndPostResponse(checks,sus_score,url,tweet,test=False):
	# First count the number of failed checks

	total_checks = 7
	failed_checks = 0
	max_sus_score = 0
	formatted_url = url.replace('.','[.]')
	reasons = set()
	for check in checks:
		if checks[check]['status'] == 'FAIL':
			failed_checks+=1
		else:
			max_sus_score+=checks[check]['MAX_SUS_SCORE']
			if checks[check]['status'] == 'NOK':
				# max_sus_score+=checks[check]['MAX_SUS_SCORE']
				for reason in checks[check]['description']:
					reasons.add(reason)
	

	logging.info(f"Final SUS Score {sus_score}")
	logging.info(f"Max SUS Score {max_sus_score}")

	tweet_text = ""
	if failed_checks>=4:
		# So many failed checks, so can't come up with a decision
		tweet_text = f"Sorry, I am not able to come up with a decision for the site ({formatted_url}) because majority of checks failed to run on my backend. You can report this to my author (@techraj156)"
		if test:
			return {'tweet_text':tweet_text}
		tweet_id = tweet['tweet_id']
		postTweet(tweet_text=tweet_text,reply_to=tweet_id)
		return
			
	
	if max_sus_score<=10:
		tweet_text = f"Scan results for {formatted_url}\n"
		tweet_text+= f"Site looks SAFE. \nBut remember - if you feel something is too good to be true, it is probably just a scam."
		if test:
			return {'tweet_text':tweet_text}
		new_tweet_id = postTweet(tweet_text=tweet_text,reply_to=tweet_id)
		tweet_id = tweet['tweet_id']
		tweet_author_username = tweet['tweet_author_username']
		tweet_author_id = tweet['tweet_author_id']
		scanned_url = tweet['url']
		if new_tweet_id is not None:
			# Add to DB
			addToDB(tweet_id=new_tweet_id, tweet_author_username=tweet_author_username, tweet_author_id=tweet_author_id, url=scanned_url, results=checks)
		return
		
	else:
		sus_percentage = math.ceil((sus_score*100)/(max_sus_score))
		tweet_text = ""

		logging.info(f"SUS Percentage {sus_percentage}%")

		if sus_percentage<25:
			# looks safe
			tweet_text = f"Scan results for {formatted_url}\n"
			tweet_text+= f"Site looks SAFE. \nBut remember - if you feel something is too good to be true, it is probably just a scam."

		elif sus_percentage>=25 and sus_percentage<50:
			# look sus
			tweet_text = f"Scan results for {formatted_url}\n"
			tweet_text+= f"Site looks SUSPICIOUS\n"
			for reason in reasons:
				tweet_text+= f"- {reason}\n"
		
		elif sus_percentage>=50 and sus_percentage<75:
			# probably scam
			tweet_text = f"Scan results for {formatted_url}\n"
			tweet_text+="Site is probably SCAM\n"
			for reason in reasons:
				tweet_text+= f"- {reason}\n"
		elif sus_percentage>=75:
			# site is scam
			tweet_text = f"Scan results for {formatted_url}\n"
			tweet_text+="Site is SCAM\n"
			for reason in reasons:
				tweet_text+= f"- {reason}\n"

		if test:
			return {'tweet_text':tweet_text,'sus_percentage':sus_percentage,'sus_score':sus_score,'max_sus_score':max_sus_score}
		
		tweet_id = tweet['tweet_id']
		tweet_author_username = tweet['tweet_author_username']
		tweet_author_id = tweet['tweet_author_id']
		scanned_url = tweet['url']
		new_tweet_id = postTweet(tweet_text, tweet_id)
		if new_tweet_id is not None:
			addToDB(tweet_id=new_tweet_id, tweet_author_username=tweet_author_username, tweet_author_id=tweet_author_id, url=scanned_url, results=checks)


def parseTweets(tweets,test=False):
	# print(tweets)
	# First check if there are any new tweets
	if not "data" in tweets:
		# print("there are no new tweets")
		logger.info("No new tweets found")
		return
	
	newest_tweet_id = tweets['meta']['newest_id']
	last_mentioned_tweet_path = os.path.join(BASE_DIR,"tmp","lastmentionedtweet")
	if not test:
		# Add newest tweet to file
		f= open(last_mentioned_tweet_path,"w")
		f.write(newest_tweet_id)
		f.close()
		logger.info(f"Added newest_tweet_id {newest_tweet_id} to 'tmp/lastmentionedtweet'")

	for ind, tweet in enumerate(tweets['data']):
		logger.info(f"Processing tweet {tweet}")
		tweet_text = tweet['text']
		tweet_id = tweet['id']
		tweet_author_id = tweet['author_id']
		tweet_author_username = ""

		# Check if tweet is a reply or retweet
		if 'referenced_tweets' in tweet:
			# it is a reply or rt, don't process
			continue

		for author in tweets['includes']['users']:
			if author['id'] == tweet_author_id:
				tweet_author_username = author['username']
				break
		
		if MAINTENANCE_MODE == 'ON':
			maintenance(reply_to=tweet_id)
			continue
		
		regex = "http[s]?[z]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
		url = re.findall(regex,tweet_text)
		if len(url)==0:
			logger.info(f"No valid URL found in tweet")
			continue
		url = url[0]
		url = url.replace("httpz","https")
		logger.info(f"Extracted URL {url}")

		if test:
			return url

		if "t.co" in url:
			# wrapped in t.co URL, so resolve
			url = resolveTwitterURL(url)

		if url is None:
			logging.info("Ignoring tweet because unable to resolve")
			continue

		logger.info(f"Final URL after resolving {url}")
		# print(f"Final URL after resolving {url}")

		formatted_url = url.replace('.','[.]')

		# Check if the site is whitelisted
		whitelisted = checkWhitelist(url)
		if whitelisted:
			tweet_text = f"Site {formatted_url} is in Whitelist, hence skipping scans as it is assumed to be SAFE.\n"
			tweet_text+="But remember - if you feel something is too good to be true, it is probably just a scam."
			tweet_id = postTweet(tweet_text=tweet_text, reply_to=tweet_id)
			continue

		# Check in DB
		checked = checkInDB(url)
		if checked is not None:
			tweet_text = f"Scan for {formatted_url} is already made in the past\n"
			tweet_text+=f"https://twitter.com/twitter/statuses/{checked}"
			postTweet(tweet_text=tweet_text,reply_to=tweet_id)
			continue

		connectivity = checkConnectivity(url)

		if connectivity[0]==False:
			logger.info("Cannot connect to target URL so not performing checks")
			logger.info(f"Reason: {connectivity[1]}")
			formatted_url = url.replace(".","[.]")
			tweet_text = f"@{tweet_author_username}\nCould not connect to the URL ({formatted_url})"
			tweet_text+=f"\n- {connectivity[1]}"
			postTweet(tweet_text=tweet_text,reply_to=tweet_id)
			return
		
		# print("Connection OK")
		# print("Performing checks")
		results = performChecks(url)
		checks = results[0]
		sus_score = results[1]

		print("CHECKS: ",checks)
		print("sus score: ",sus_score)

		tweet = {'tweet_id':tweet_id, 'tweet_author_username':tweet_author_username, 'tweet_author_id':tweet_author_id, 'url':url}

		analyzeAndPostResponse(checks,sus_score,url,tweet)


def maintenance(reply_to):
	logger.info("MAINTENANCE MODE ON")
	tweet_text = "Bot is currently in maintenance, scan will be performed once bot is back online."
	postTweet(tweet_text=tweet_text, reply_to=reply_to)


def main():
	global WAIT_TIME
	global MAINTENANCE_MODE
	print("Monitoring tweets! - PROGRAM STARTED")
	count = 0
	while 1:
		count+=1
		logger.info(f"Round {count} - Checking for mentioned tweets")
		print(f"Round {count} - Checking for mentioned tweets")
		tweets = None
		if not os.path.exists(os.path.join(BASE_DIR,"tmp")):
			logger.info(f"Did not find directory 'tmp', creating now")
			os.mkdir(os.path.join(BASE_DIR,"tmp"))
			f = open(os.path.join(BASE_DIR,"tmp","lastmentionedtweet"),"w")
			f.write("")
			f.close()
			logger.info(f"Created file 'tmp/lastmentionedtweet'")
			# print(f"Created file 'tmp/lastmentionedtweet'")
			tweets = client.get_users_mentions(id=USER_ID, expansions="author_id")
		elif not os.path.exists(os.path.join(BASE_DIR,"tmp","lastmentionedtweet")):
			f = open(os.path.join(BASE_DIR,"tmp","lastmentionedtweet"),"w")
			f.write("")
			f.close()
			logger.info(f"Created file 'tmp/lastmentionedtweet'")
			tweets = client.get_users_mentions(id=USER_ID, expansions="author_id")
		else:
			f = open(os.path.join(BASE_DIR,"tmp","lastmentionedtweet"),"r")
			recent_tweet = f.read().strip()
			f.close()
			logger.info(f"Retrieved recent tweet_id {recent_tweet} from 'tmp/lastmentionedtweet'")
			if recent_tweet!="":
				tweets = client.get_users_mentions(id=USER_ID, since_id=recent_tweet, expansions=["referenced_tweets.id","author_id"])
			else:
				tweets = client.get_users_mentions(id=USER_ID, expansions=["referenced_tweets.id","author_id"])

		parseTweets(tweets=tweets)
		time.sleep(WAIT_TIME*60)



if __name__ == "__main__":
	main()