import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import os
import numpy as np

collection = "flickr_crawler_4_v2"
client = MongoClient()
db = client.twitterdb

group_by_year = db[collection].aggregate([
    {
        '$group': {
            "_id": { 
                "y": {'$year': '$dateupload'},
            },
            "total": {'$sum': 1},
            "geo": {"$sum": "$geo_is_public"},
            "uniqueIds": {"$addToSet": "$id"},
        }
    }, 
    {
        '$sort':{
            "_id":1
        }
    }     
    ])

year = []
count = []
unique = []
geo = []
for group in group_by_year:
    year.append(group["_id"]["y"])
    count.append(group["total"])
    unique.append(len(group["uniqueIds"]))
    geo.append(group["geo"])

year = np.array(year)
count = np.array(count)
unique = np.array(unique)
geo = np.array(geo)
plt.figure()
bar_width = 0.2
plt.bar(year-bar_width, count, align='center', label="Total", width=bar_width)
plt.bar(year, unique, align='center', label="Unique", width=bar_width)
plt.bar(year+bar_width, geo, align='center', label="Geo-tagged", width=bar_width)
plt.xticks(year, year)
plt.xticks(rotation=90)
plt.xlabel("Year")
plt.ylabel("Number of Photos")
plt.title("Uploads to Flickr by Year")
plt.legend()
plt.tight_layout()
plt.savefig(os.getcwd() + "/year_flickr.svg", format='svg', dpi=1200)
plt.show()