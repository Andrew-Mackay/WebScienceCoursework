'''
2. Develop basic data analytics
'''
import config
from pymongo import MongoClient

#---------------------- 2a. -----------------
collections = {"basic_crawler_1a": {}, "enhanced_crawler_1b":{}, "geo_tagged_1c":{}}
total_tweets = 0
total_geo = 0
client = MongoClient()
db = client.twitterdb

for collection_name, collection in collections.items():
    total = db[collection_name].count()
    total_tweets += total
    collection["total"] = total
    geo_tagged = db[collection_name].count_documents({"geo": {"$ne" : None}})
    total_geo += geo_tagged
    collection["geo_tagged"] = geo_tagged
    print("Collection: ", collection_name)
    print("    Total tweets: ", total)
    print("    Geo-tagged tweets: ", geo_tagged)
    print("    Geo-tagged: ", "{0:.2f}".format((geo_tagged/total) * 100), "%")
    print(" ")

print(" ")
print("-------Summary--------")
print("Total tweets collected: ", total_tweets)
print("Geo-tagged tweets collected: ", geo_tagged)
print("Geo-tagged: ", "{0:.2f}".format((total_geo/total_tweets) * 100), "%")

#---------------------- 2b. -----------------

