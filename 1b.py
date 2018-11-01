'''
1b. Enhance the crawling using Streaming % REST API
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time
import common_words


client = MongoClient()
db = client.twitterdb
found_first_tweet = False
first_tweet = None


class Listener(tweepy.StreamListener):
    def on_status(self, status):
        global found_first_tweet, first_tweet
        if not found_first_tweet:
            first_tweet = status
            found_first_tweet = True

        db.not_geo.insert(status._json)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
        print(status_code)
        # returning non-False reconnects the stream, with backoff.

def insert_search_results_to_db(search_results):
    for result in search_results:
        print(result)
        db.rest_collection.insert(result._json)


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

twitterStream = tweepy.Stream(auth, Listener())
api = tweepy.API(auth)
# trends_available = api.trends_available() # returns ids
# print(trends_available)
# trends_place = api.trends_place(id)
# trend_clostest = api.trend_clostest(lat, long)
twitterStream.sample(languages=["en"], async=True)

# Wait until first tweet is found from stream (maybe use wait instead of pass?)
while not found_first_tweet:
    pass


# while True:
search = api.search("bike", lang="en", since_id=first_tweet.id)
insert_search_results_to_db(search)