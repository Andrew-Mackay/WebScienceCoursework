'''
1c. Grab as much geo-tagged data for Glasgow/Singapore
for the same period 
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time
import queue

RUN_TIME = 30  # how long program should run for (in minutes)
GLASGOW_WOEID = 21125  # WOEID for Glasgow
GEOBOX_GLASGOW = [-4.359484911, 55.8030299038, -4.1260254383, 55.9101684715]  # taken from https://boundingbox.klokantech.com/
MAX_TWEETS_PER_TREND = 40000  # Only take this many tweets per trend (helps to ensure a balance of tweets)
COLLECTION_NAME = "geo_tagged_1c"

users_with_geo_tagged_tweets = queue.Queue()

client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_status(self, status):
        global users_with_geo_tagged_tweets
        users_with_geo_tagged_tweets.put(status.user.id)
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


# Returns False if time has expired, True otherwise
def process_user(api, collection, end_time, user_id):
    for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
        if status.geo_enabled == True:
            db[collection].insert(status._json)

        # Quit if run for over 1 hour
        if time.time() > end_time:
            return False
    return True
    # maybe if 10 not geo in a row break?

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

time_end = time.time() + 60 * RUN_TIME

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.filter(languages=["en"], async=True, locations=GEOBOX_GLASGOW)

api = tweepy.API(auth, wait_on_rate_limit=True)

while True:
    if not users_with_geo_tagged_tweets.empty():
        if not process_user(api, COLLECTION_NAME, time_end, users_with_geo_tagged_tweets.get()):
            twitterStream.disconnect()
            exit()
        
    # Quit if run for over time period hour
    if time.time() > end_time:
        twitterStream.disconnect()
        exit()

glasgow_trends = api.trends_place(GLASGOW_WOEID)  # get trends in Glasgow
glasgow_trends = glasgow_trends[0]['trends']  # Extract information
sorted_glasgow_trends = sorted(glasgow_trends, key=lambda k: sorted_helper(k['tweet_volume']), reverse=True)  # sort trends by tweet volume
# print(uk_trends)
for trend in sorted_glasgow_trends:
    tweets_collected = 0
    print(trend["name"], trend["tweet_volume"])

    for status in tweepy.Cursor(api.search, q=trend["name"], rpp=100, lang="en").items():
        tweets_collected += 1
        if status.geo_enabled == True:
            db[COLLECTION_NAME].insert(status._json)
        # Move to next trend when collected enough from this trend
        if tweets_collected > MAX_TWEETS_PER_TREND:
            break
        
        # Quit if run for over 1 hour
        if time.time() > time_end:
            twitterStream.disconnect()
            exit()