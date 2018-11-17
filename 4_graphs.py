import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import os
import numpy as np
import pandas as pd


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

def to_date(row):
    return row[0].generation_time
    
df = pd.DataFrame(list(db[collection].find({}, {"_id":1})))
df["created_date"] = df.apply (lambda row: to_date (row),axis=1)
agg_10m = df.groupby(pd.Grouper(key="created_date", freq='10Min')).size()
photos_per_10m = agg_10m.values.tolist()[:-1]
x_labels = range(0, 70, 10)

plt.figure()
plt.bar(range(len(photos_per_10m)), photos_per_10m, align='edge')
plt.xticks(range(len(x_labels)), x_labels)
plt.xlabel("Elapsed Time (Minutes)")
plt.ylabel("Number of Photos")
plt.title("Distribution of Photos Collected Over 1 Hour")
plt.tight_layout()

plt.savefig(os.getcwd() + "/hour_flickr.svg" , format='svg', dpi=1200)
plt.show()