# Flickr crawler

import config_flickr
from pymongo import MongoClient
import json
import time
import queue
import _thread
from datetime import datetime
from datetime import timedelta
import flickrapi

RUN_TIME = 59  # how long program should run for (in minutes)
COLLECTION_NAME = "flickr_crawler_4"
time_expired = False
EXTRAS = ["date_upload", "date_taken", "owner_name", "geo", "tags", "o_dims", "views", "media"]

users_to_process = queue.Queue()

client = MongoClient()
db = client.twitterdb
collection = db[COLLECTION_NAME]

flickr = flickrapi.FlickrAPI(config_flickr.KEY, config_flickr.SECRET, format='parsed-json')

# Get all recent photos from flickr
page = 1
pages = 1
recent_photos = []
while(page <= pages):
  recent_photos_results = flickr.photos.getRecent(extras=EXTRAS, page=page, per_page=500)["photos"]
  recent_photos.extend(recent_photos_results["photo"])
  pages = recent_photos_results["pages"]
  page += 1

print("Number of photos collected: ", len(recent_photos))
for photo in recent_photos:
  # insert into DB
  collection.insert(photo)
  # add user to Queue
  users_to_process.put(photo["owner"])

print(users_to_process)



# hot_tags = flickr.tags.getHotList(count=200)["hottags"]["tag"]
# for tag in hot_tags:
#   print(tag["_content"])
#   clusters = flickr.tags.getClusters(tag=tag["_content"])["clusters"]
#   print(clusters["cluster"])


# print(flickr.panda.getList())
# # print(flickr.trait_names())
# photos = flickr.panda.getPhotos(panda_name="wang wang", extras=["date_upload", "date_taken", "owner_name", "geo", "tags", "views", "media"])
# print(flickr.panda.getPhotos(panda_name="ling ling"))
# print(flickr.panda.getPhotos(panda_name="hsing hsing"))
# print(photos.tag)
# for child in photos:
#   print(child.tag, child.attrib)
