'''
1a. Use streaming API (gardenhose api) for collecting 1% data
'''
import config
from pymongo import MongoClient
import tweepy
import json


client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_data(self, raw_data):
        print(raw_data)
        data_json = json.loads(raw_data)
        db.sampleCollection.insert(data_json)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
        print(status_code)
        # returning non-False reconnects the stream, with backoff.


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

twitterStream = tweepy.Stream(auth, Listener())
# Stream English tweets
twitterStream.sample(languages=["en"])
