'''
1b. Enhance the crawling using Streaming % REST API
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time
import _thread

RUN_TIME = 30  # how long program should run for (in minutes)
UK_WOEID = 	23424975  # WOEID for United Kingdom, used for finding trends
MAX_TWEETS_PER_TREND = 40000  # Only take this many tweets per trend (helps to ensure a balance of tweets)
COLLECTION_NAME = "enhanced_crawler_1b"
time_expired = False

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


def user_based_probes(threadName):
    print(threadName + " Started.")
    while not time_expired:
        # TODO implement
        pass

def sorted_helper(tweet_volume):
    # if no tweet_volume information is available set to 0
    if tweet_volume is None:
        return 0
    return tweet_volume

def trend_based_probes(threadName):
    print(threadName + " Started.")
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
            if tweets_collected > MAX_TWEETS_PER_TREND or time_expired:
                break
        if time_expired:
            break

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

time_end = time.time() + 60 * RUN_TIME

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.sample(languages=["en"], async=True)

api = tweepy.API(auth, wait_on_rate_limit=True)

# User based probes and keyword based probes handled on seperate threads
try:
   user_thread = _thread.start_new_thread(user_based_probes, ("User_thread",))
   trend_thread = _thread.start_new_thread(trend_based_probes, ("Trend-thread",))
except:
   print("Error: unable to start thread")

while time.time() < time_end:
    time.sleep(10)

time_expired = True

# Time expired
twitterStream.disconnect()
