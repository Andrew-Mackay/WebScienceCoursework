'''
2. Develop basic data analytics
'''
import config
from pymongo import MongoClient

print("---------------------- Flickr Analysis-----------------")

collection = "flickr_crawler_4_v2"
client = MongoClient()
db = client.twitterdb

total_collected = db[collection].count()
geo_tagged = db[collection].count_documents({"geo_is_public": 1})

print("Total Photos: ", total_collected)
print("Geo-tagged Photos: ", geo_tagged)
print("Geo-tagged: ", "{0:.2f}".format((geo_tagged/total_collected) * 100), "%\n")

x = db[collection].aggregate([
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
print("Number of Duplicates: ", number_of_duplicates, "\n")

x = db[collection].find({}, {"views":1, "_id":0, "id":1})
total_views = 0
max_views = 0
max_id = None
for picture in x:
    pic_views = int(picture["views"])
    if pic_views > max_views:
        max_views = pic_views
        max_id = picture["id"]
    total_views += pic_views

print("Total photo views: ", total_views)
print("Average views per photo: ", "{0:.4f}".format((total_collected/total_views)))
print("Most views for an individual photo:", max_views, ". Flickr ID:", max_id, " URL: www.flickr.com/photo.gne?id="+max_id)