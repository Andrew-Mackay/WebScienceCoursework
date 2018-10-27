import config
from pymongo import MongoClient
import tweepy
import json

RUN_TIME = 1  # run collection for 1 hour
client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_data(self, raw_data):
        print(raw_data)
        data_json = json.loads(raw_data)
        db.not_geo.insert(data_json)
        return True

    def on_error(self, status_code):
        print(status_code)


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

twitterStream = tweepy.Stream(auth, Listener())
# twitterStream.filter(track=["car"])
twitterStream.sample()
