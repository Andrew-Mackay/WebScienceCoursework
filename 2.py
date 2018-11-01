'''
2. Develop basic data analytics
'''
import config
from pymongo import MongoClient

print("---------------------- 2a. -----------------")
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
    print("    Geo-tagged: ", "{0:.2f}".format((geo_tagged/total) * 100), "%\n")

print("\nSummary")
print("    Total tweets collected: ", total_tweets)
print("    Geo-tagged tweets collected: ", geo_tagged)
print("    Geo-tagged: ", "{0:.2f}".format((total_geo/total_tweets) * 100), "%")

print("\n---------------------- 2b. -----------------")
total = db.enhanced_crawler_1b.count()
print("Geo-tagged data from Glasgow: ", total)
overlap = 0
for tweet in db.basic_crawler_1a.find():
     if db.geo_tagged_1c.count_documents({"id":tweet["id"]}) > 0:
         overlap += 1
print("Number of tweets common to both geo-tagged Glasgow and 1%: ", overlap)

print("\n---------------------- 2c. -----------------")
for collection_name, collection in collections.items():
    x = db[collection_name].aggregate([
        {"$group": {
            "_id": {"id": "$id"},
            "uniqueIds": {"$addToSet": "$_id"},
            "count": {"$sum": 1} 
            } 
        }, 
        {"$match": { 
            "count": {"$gte": 2 } 
            }
        },
        {"$sort" : {"count" : -1} }
      ])
    number_of_duplicates = 0
    for y in x:
        number_of_duplicates += y["count"]
    print("Collection: ", collection_name)
    print("    Number of Duplicates: ", number_of_duplicates, "\n")
