'''
1a. Use streaming API (gardenhose api) for collecting 1% data
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time
from datetime import datetime
from datetime import timedelta


RUN_TIME = 59  # how long program should run for (in minutes)
COLLECTION_NAME = "basic_crawler_1a"

client = MongoClient()
db = client.twitterdb

def convert_to_datetime(status):
    json_tweet = status._json
    json_tweet["created_at"] = datetime.strptime(json_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    return json_tweet

class Listener(tweepy.StreamListener):
    def on_status(self, status):
        db[COLLECTION_NAME].insert(convert_to_datetime(status))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
        print(status_code)
        # returning non-False reconnects the stream, with backoff.


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

start_time = datetime.now()
time_end =  start_time + timedelta(minutes=RUN_TIME)

twitterStream = tweepy.Stream(auth, Listener())
# Stream English tweets
twitterStream.sample(languages=["en"], async=True)

while datetime.now() < time_end:
    # sleep 30 seconds to avoid excess loop iterations
    time.sleep(30)

twitterStream.disconnect()
print("Start Time: ", start_time)
print("End Time: ", time_end)


