# Program to generate random 5% of data for submission.

from pymongo import MongoClient
import random

client = MongoClient()
db = client.twitterdb
twitter_collection = db["enhanced_crawler_1b"]
flickr_collection = db["flickr_crawler_4_v2"]
new_sample_twitter = db["twitter_sample"] # 5% of enhanced 1b collection
new_flickr_sample = db["flickr_sample"] # 5% of flickr collection

total_twitter = twitter_collection.count()
total_flickr = flickr_collection.count()
print(total_twitter, total_flickr)
sample_size_twitter = (total_twitter/100) * 5
sample_size_flickr = (total_flickr/100) * 5
print(sample_size_twitter, sample_size_flickr)

for tweet in twitter_collection.find():
  if random.randint(1, 101) <= 5:
    new_sample_twitter.insert(tweet)

for photo in flickr_collection.find():
  if random.randint(1, 101) <= 5:
    new_flickr_sample.insert(photo)

print(new_sample_twitter.count())
print(new_flickr_sample.count())




