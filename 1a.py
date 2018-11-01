'''
1a. Use streaming API (gardenhose api) for collecting 1% data
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time


RUN_TIME = 60  # how long program should run for (in minutes)
COLLECTION_NAME = "basic_crawler_1a"

client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_status(self, status):
        # global found_first_tweet, first_tweet
        db[COLLECTION_NAME].insert(status._json)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
        print(status_code)
        # returning non-False reconnects the stream, with backoff.


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

time_end = time.time() + 60 * RUN_TIME

twitterStream = tweepy.Stream(auth, Listener())
# Stream English tweets
twitterStream.sample(languages=["en"], async=True)

while time.time() < time_end:
    # sleep 30 seconds to avoid excess loop iterations
    time.sleep(30)

twitterStream.disconnect()
exit()



