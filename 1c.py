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
import _thread

RUN_TIME = 2  # how long program should run for (in minutes)
GLASGOW_WOEID = 21125  # WOEID for Glasgow
GEOBOX_GLASGOW = [-4.359484911, 55.8030299038, -4.1260254383, 55.9101684715]  # taken from https://boundingbox.klokantech.com/
GLASGOW_GEOCODE = "55.86515,-4.25763,6km"  # taken from http://latitudelongitude.org/gb/glasgow/
COLLECTION_NAME = "geo_tagged_1c"
time_expired = False
user_thread_finished = False
trend_thread_finished = False
keyword_thread_finished = False

users_with_geo_tagged_tweets = queue.Queue()

client = MongoClient()
db = client.twitterdb


class Listener(tweepy.StreamListener):
    def on_status(self, status):
        global users_with_geo_tagged_tweets
        users_with_geo_tagged_tweets.put(status.user.id)
        db[COLLECTION_NAME].insert(status._json)
        print("+1 stream tweet added")
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
        print(status_code)
        # returning non-False reconnects the stream, with backoff.


def process_user(user_id):
    for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
        if status.geo is not None:
            db[COLLECTION_NAME].insert(status._json)
            print("+1 user tweet added")
        if time_expired:
            break
    # maybe if 10 not geo in a row break?

def user_based_probes(threadName):
    print(threadName + " Started.")
    while not time_expired:
        if not users_with_geo_tagged_tweets.empty():
            process_user(users_with_geo_tagged_tweets.get())

def sorted_helper(tweet_volume):
    # if no tweet_volume information is available set to 0
    if tweet_volume is None:
        return 0
    return tweet_volume

def trend_based_probes(threadName):
    print(threadName + " Started.")
    glasgow_trends = api.trends_place(GLASGOW_WOEID)  # get trends in Glasgow
    glasgow_trends = glasgow_trends[0]['trends']  # Extract information
    sorted_glasgow_trends = sorted(glasgow_trends, key=lambda k: sorted_helper(k['tweet_volume']), reverse=True)  # sort trends by tweet volume
    for trend in sorted_glasgow_trends:
        print(trend["name"], trend["tweet_volume"])
        for status in tweepy.Cursor(api.search, q=trend["name"], rpp=100, lang="en", geocode=GLASGOW_GEOCODE).items():
            if status.geo is not None:
                db[COLLECTION_NAME].insert(status._json)
                print("+1 trend tweet added")
            if time_expired:
                break
        if time_expired:
            break

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

time_end = time.time() + 60 * RUN_TIME

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.filter(languages=["en"], async=True, locations=GEOBOX_GLASGOW)

api = tweepy.API(auth, wait_on_rate_limit=True)

# User based probes and keyword based probes handled on seperate threads
try:
   _thread.start_new_thread(user_based_probes, ("User_thread", ))
   _thread.start_new_thread(trend_based_probes, ("Trend-thread", ))
except:
   print("Error: unable to start thread")

while time.time() < time_end:
    time.sleep(10)

time_expired = True

# Time expired
twitterStream.disconnect()




