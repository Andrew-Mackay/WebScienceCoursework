'''
1b. Enhance the crawling using Streaming & REST API
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time
import _thread
from datetime import datetime
from datetime import timedelta


RUN_TIME = 30  # how long program should run for (in minutes)
UK_WOEID = 	23424975  # WOEID for United Kingdom, used for finding trends
MAX_TWEETS_PER_TREND = 40000  # Only take this many tweets per trend (helps to ensure a balance of tweets)
COLLECTION_NAME = "enhanced_crawler_1b"
time_expired = False

users_to_process = queue.Queue()

client = MongoClient()
db = client.twitterdb

def convert_to_datetime(status):
    json_tweet = status._json
    json_tweet["created_at"] = datetime.strptime(json_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    return json_tweet

class Listener(tweepy.StreamListener):
    def on_status(self, status):
        global users_to_process
        users_to_process.put(status.user.id)
        db[COLLECTION_NAME].insert(convert_to_datetime(status))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
        print(status_code)
        # returning non-False reconnects the stream, with backoff.


def process_user(user_id):
    non_geo_count = 0  # Used to break from users who have many non geo tweets in a row
    break_count = 5
    for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
        if status.geo is not None:
            db[COLLECTION_NAME].insert(convert_to_datetime(status))
            print("+1 user tweet added")
        else:
            non_geo_count += 1

        if time_expired or non_geo_count > break_count:
            break

def user_based_probes(threadName):
    print(threadName + " Started.")
    while not time_expired:
        if not users_to_process.empty():
            process_user(users_to_process.get())

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
            db[COLLECTION_NAME].insert(convert_to_datetime(status))
            # Move to next trend when collected enough from this trend
            if tweets_collected > MAX_TWEETS_PER_TREND or time_expired:
                break
        if time_expired:
            break

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

start_time = datetime.now()
time_end =  start_time + timedelta(minutes=RUN_TIME)

twitterStream = tweepy.Stream(auth, Listener())
twitterStream.sample(languages=["en"], async=True)

api = tweepy.API(auth, wait_on_rate_limit=True)

# User based probes and keyword based probes handled on seperate threads
try:
   user_thread = _thread.start_new_thread(user_based_probes, ("User_thread",))
   trend_thread = _thread.start_new_thread(trend_based_probes, ("Trend-thread",))
except:
   print("Error: unable to start thread")

while datetime.now() < time_end:
    time.sleep(10)
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
