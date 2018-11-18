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


RUN_TIME = 60  # how long program should run for (in minutes)
COLLECTION_NAME = "basic_crawler_1a" # Name of collection to save tweets to

# Setup database connection
client = MongoClient()
db = client.twitterdb

# Converts a tweets created_at field to a python datetime object
def convert_to_datetime(status):
    json_tweet = status._json
    json_tweet["created_at"] = datetime.strptime(json_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    return json_tweet

# Used for streaming
class Listener(tweepy.StreamListener):
    def on_status(self, status):
        # when a new tweet comes in the stream, add to the database
        db[COLLECTION_NAME].insert(convert_to_datetime(status))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # disconnects the stream
            return False
        print(status_code)
        # reconnects the stream, with backoff.


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

# Used for timing the stream to only last RUN_TIME
start_time = datetime.now()
time_end =  start_time + timedelta(minutes=RUN_TIME)

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.sample(languages=["en"], async=True) # Stream English tweets

while datetime.now() < time_end:
    # sleep 30 seconds to avoid excess loop iterations
    time.sleep(30)

twitterStream.disconnect()
print("Start Time: ", start_time)
print("End Time: ", time_end)


