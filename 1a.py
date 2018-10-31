import config
from pymongo import MongoClient
import tweepy
import json
import time
import common_words
RUN_TIME = 60  # specify value in minutes
client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_data(self, raw_data):
        print(raw_data)
        data_json = json.loads(raw_data)
        db.not_geo.insert(data_json)
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
# Use filter with 100 most common English words instead of sample to ensure language is English
twitterStream.filter(track=common_words.most_common_words, languages=["en"])

# maybe inclue stream disconnect?
