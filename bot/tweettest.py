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


def postTweet(tweet_text, reply_to=""):
    try:
        if reply_to == "":
            print(client.create_tweet(text = tweet_text))
        else:
            client.create_tweet(text = tweet_text, in_reply_to_tweet_id= reply_to)
        return [1]
    except Exception as e:
        print("EXCEPTION OCCURED: ",e)
        return [0,e]



def retrieveTweet(tweet_id):
    try:
        status = client.get_tweet(id=tweet_id)
        return status['data']
    except Exception as e:
        logging.error("Exception occured in retrieveTweet")
        logging.error(str(e))
        return None
    
        


# postTweet("HELLO")
# print(retrieveTweet("1544527288049750017"))