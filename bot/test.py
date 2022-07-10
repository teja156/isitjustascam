import tweepy
import os
import json



base_path = os.getcwd()
f=open(base_path+"/creds/twittercreds.json","r")
data = json.loads(f.read())
f.close()


BEARER_TOKEN = data['BEARER_TOKEN']
API_KEY = data['API_KEY']
API_KEY_SECRET = data['API_KEY_SECRET']
ACCESS_TOKEN = data['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
USER_ID = data['USER_ID']
BOT_USERNAME = data['BOT_USERNAME']

client = tweepy.Client(bearer_token=BEARER_TOKEN, 
                        consumer_key=API_KEY, 
                        consumer_secret=API_KEY_SECRET, 
                        access_token=ACCESS_TOKEN, 
                        access_token_secret=ACCESS_TOKEN_SECRET, 
                        return_type = dict,
                        wait_on_rate_limit=True)


tweets = client.get_users_mentions(id=USER_ID, expansions="author_id", since_id="1544524936328273920")

print(tweets)