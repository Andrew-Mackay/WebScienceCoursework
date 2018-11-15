# Flickr crawler

import config_flickr
from pymongo import MongoClient
import time
import queue
from datetime import datetime
from datetime import timedelta
import flickrapi

RUN_TIME = 59  # how long program should run for (in minutes)
COLLECTION_NAME = "flickr_crawler_4"
time_expired = False
EXTRAS = ["date_upload, date_taken, owner_name, geo, tags, o_dims, views, media"]
MAX_QUERIES = 3500 # Flickr limit is 3600 per hour but reduced to 3500 to ensure safe limit

users_to_process = queue.Queue()

client = MongoClient()
db = client.twitterdb
collection = db[COLLECTION_NAME]

queries_made = 0
flickr = flickrapi.FlickrAPI(config_flickr.KEY, config_flickr.SECRET, format='parsed-json')

def insert_into_db(photos, add_user=False):
  for photo in photos:
    collection.insert(photo)
    if add_user:
      users_to_process.put(photo["owner"])


# Get all recent photos from flickr
page = 1
pages = 1
while(page <= pages and queries_made < MAX_QUERIES):
  photos = flickr.photos.getRecent(extras=EXTRAS, page=page, per_page=500)["photos"]
  queries_made += 1
  insert_into_db(photos["photo"], add_user=True)
  pages = photos["pages"]
  page += 1
  break

# Search over the hottest tags for photos
hot_tags = flickr.tags.getHotList(count=200)["hottags"]["tag"]
queries_made += 1
for tag in hot_tags:
  tag = tag["_content"]
  page = 1
  pages = 1
  while(page <= pages and queries_made < MAX_QUERIES):
    photos = flickr.photos.search(tags=tag, tag_mode="all",extras=EXTRAS, page=page, per_page=500)["photos"]
    queries_made += 1
    insert_into_db(photos["photo"], add_user=True)
    pages = photos["pages"]
    page += 1
    break
  break


# Get all users public photos
while(not users_to_process.empty()):
  user = users_to_process.get()
  page = 1
  pages = 1
  while(page <= pages and queries_made < MAX_QUERIES):
    photos = flickr.people.getPublicPhotos(user_id=user, extras=EXTRAS, per_page=500, page=page)["photos"]
    queries_made += 1
    insert_into_db(photos["photo"])
    pages = photos["pages"]
    page += 1
    break
  break


