from tkinter.tix import TCL_WINDOW_EVENTS
import tweepy
import requests
import os
import json
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)


load_dotenv()

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
USER_ID = os.getenv("USER_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")


client = tweepy.Client( bearer_token=BEARER_TOKEN, 
                        consumer_key=API_KEY, 
                        consumer_secret=API_KEY_SECRET, 
                        access_token=ACCESS_TOKEN, 
                        access_token_secret=ACCESS_TOKEN_SECRET, 
                        return_type = dict,
                        wait_on_rate_limit=True)



def mentionTest(since_id):
    tweets = client.get_users_mentions(id=USER_ID, since_id=since_id, expansions=["referenced_tweets.id","author_id"])
    return tweets

def getTweet(tweet_id):
    tweet = client.get_tweet(id=tweet_id, expansions=["referenced_tweets.id","author_id"])
    return tweet


# print(mentionTest("1556919637979254784"))
print("Original tweet: ")
print(getTweet("1556173277835546625"))
print()
print("Replied Tweet: ")
print(getTweet("1556437707034791936"))




    