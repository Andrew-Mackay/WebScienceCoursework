import config
from pymongo import MongoClient
import tweepy

client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_data(self, raw_data):
        print(raw_data)
        return True

    def on_error(self, status_code):
        print(status_code)


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.filter(track=["car"])
