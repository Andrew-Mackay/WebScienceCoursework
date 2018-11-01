'''
1b. Enhance the crawling using Streaming % REST API
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time

RUN_TIME = 30  # how long program should run for (in minutes)
UK_WOEID = 	23424975  # WOEID for United Kingdom, used for finding trends
MAX_TWEETS_PER_TREND = 40000  # Only take this many tweets per trend (helps to ensure a balance of tweets)
COLLECTION_NAME = "enhanced_crawler_1b"

client = MongoClient()
db = client.twitterdb
# found_first_tweet = False
# first_tweet = None


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


def sorted_helper(tweet_volume):
    # if no tweet_volume information is available set to 0
    if tweet_volume is None:
        return 0
    return tweet_volume

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

time_end = time.time() + 60 * RUN_TIME

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.sample(languages=["en"], async=True)

api = tweepy.API(auth, wait_on_rate_limit=True)

uk_trends = api.trends_place(UK_WOEID)  # get trends in United Kingdom (ensures language is English and users should be awake)
uk_trends = uk_trends[0]['trends']  # Extract information
sorted_uk_trends = sorted(uk_trends, key=lambda k: sorted_helper(k['tweet_volume']), reverse=True)  # sort trends by tweet volume
# print(uk_trends)
for trend in sorted_uk_trends:
    tweets_collected = 0
    print(trend["name"], trend["tweet_volume"])

    for status in tweepy.Cursor(api.search, q=trend["name"], rpp=100, lang="en").items():
        tweets_collected += 1
        db[COLLECTION_NAME].insert(status._json)
        # Move to next trend when collected enough from this trend
        if tweets_collected > MAX_TWEETS_PER_TREND:
            break
        
        # Quit if run for over 1 hour
        if time.time() > time_end:
            twitterStream.disconnect()
            exit()