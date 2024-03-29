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
from datetime import datetime
from datetime import timedelta


RUN_TIME = 60  # how long program should run for (in minutes)
GLASGOW_WOEID = 21125  # WOEID for Glasgow
GEOBOX_GLASGOW = [-4.359484911, 55.8030299038, -4.1260254383, 55.9101684715]  # taken from https://boundingbox.klokantech.com/
GLASGOW_GEOCODE = "55.86515,-4.25763,6km"  # taken from http://latitudelongitude.org/gb/glasgow/
COLLECTION_NAME = "geo_tagged_1c" # Name of collection to save tweets to
time_expired = False

users_with_geo_tagged_tweets = queue.Queue() # used for storing twitter users

# Connect to db
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
        # add user to queue then insert tweet into db
        global users_with_geo_tagged_tweets
        users_with_geo_tagged_tweets.put(status.user.id)
        db[COLLECTION_NAME].insert(convert_to_datetime(status))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # disconnects the stream
            return False
        print(status_code)
        # reconnects the stream, with backoff.


# Process a twitter user (get all users tweets and insert into db)
def process_user(user_id):
    non_geo_count = 0  # Used to break from users who have many non geo tweets in a row
    break_count = 5
    for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
        if status.geo is not None:
            db[COLLECTION_NAME].insert(convert_to_datetime(status))
        else:
            non_geo_count += 1

        if time_expired or non_geo_count > break_count:
            break

# Thread for processing users
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

# Thread for searching for tweets based on trending topics
def trend_based_probes(threadName):
    print(threadName + " Started.")
    glasgow_trends = api.trends_place(GLASGOW_WOEID)  # get trends in Glasgow
    glasgow_trends = glasgow_trends[0]['trends']  # Extract information
    sorted_glasgow_trends = sorted(glasgow_trends, key=lambda k: sorted_helper(k['tweet_volume']), reverse=True)  # sort trends by tweet volume
    for trend in sorted_glasgow_trends:
        # search for trend in Glasgow
        for status in tweepy.Cursor(api.search, q=trend["name"], count=100, lang="en", geocode=GLASGOW_GEOCODE).items():
            if status.geo is not None:
                db[COLLECTION_NAME].insert(convert_to_datetime(status))
            if time_expired:
                break
        if time_expired:
            break

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

# Used for timing the stream to only last RUN_TIME
start_time = datetime.now()
time_end =  start_time + timedelta(minutes=RUN_TIME)

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.filter(languages=["en"], async=True, locations=GEOBOX_GLASGOW) # Stream English tweets

api = tweepy.API(auth, wait_on_rate_limit=True)

# User based probes and keyword based probes handled on seperate threads
try:
   _thread.start_new_thread(user_based_probes, ("User_thread", ))
   _thread.start_new_thread(trend_based_probes, ("Trend-thread", ))
except:
   print("Error: unable to start thread")

while datetime.now() < time_end:
    time.sleep(30)
    # Print out limits remaining for interest only, not used
    limits = api.rate_limit_status()
    resources = limits["resources"]
    searches = resources["search"]["/search/tweets"]
    application = resources["application"]["/application/rate_limit_status"]
    statuses = resources["statuses"]["/statuses/user_timeline"]
    print("Searches (Trends): ", searches)
    print("Application: ", application)
    print("Statuses (Users): ", statuses)

time_expired = True

# Time expired
twitterStream.disconnect()
print("Start Time: ", start_time)
print("End Time: ", time_end)
