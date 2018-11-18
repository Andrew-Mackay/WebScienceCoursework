# Flickr crawler

import config_flickr
from pymongo import MongoClient
import time
import queue
from datetime import datetime
from datetime import timedelta
import flickrapi

RUN_TIME = 60  # how long program should run for (in minutes)
COLLECTION_NAME = "flickr_crawler_4" # colection to store photos in
EXTRAS = ["date_upload, date_taken, owner_name, geo, tags, o_dims, views, media"]
MAX_QUERIES = 3500 # Flickr limit is 3600 per hour but reduced to 3500 to ensure safe limit
MAX_PAGES = 8 # Flickr only guarantees unique for first 4000 images in a search (500 per page -> 8 unique pages)
SLEEP_TIME = 1 # Used to prevent exceeding 1 request per second (possibly could be lowered)

client = MongoClient()
db = client.twitterdb
collection = db[COLLECTION_NAME]

users_to_process = queue.Queue()

queries_made = 0
flickr = flickrapi.FlickrAPI(config_flickr.KEY, config_flickr.SECRET, format='parsed-json')

time_expired = False
start_time = datetime.now()
end_time =  start_time + timedelta(minutes=RUN_TIME)

''' 
Insert photos into the database, if add_user is set to true, add user who took 
the photo to the user queue to be processed
'''
def insert_into_db(photos, add_user=False):
  for photo in photos:
    photo["datetaken"] = datetime.strptime(photo["datetaken"], "%Y-%m-%d %H:%M:%S")
    photo["dateupload"] = datetime.utcfromtimestamp(int(photo["dateupload"]))
    collection.insert(photo)
    if add_user:
      users_to_process.put(photo["owner"])


'''
Checks query limit and time passed to decide whether to keep running the
crawler
'''
def keep_running():
  return queries_made < MAX_QUERIES and datetime.now() < end_time


# Get all recent photos from flickr
print("Getting all recent photos... ", queries_made)
page = 1
pages = 1
while(page <= pages and page <= MAX_PAGES and keep_running()):
  try:
    photos = flickr.photos.getRecent(extras=EXTRAS, page=page, per_page=500)["photos"]
    queries_made += 1
    insert_into_db(photos["photo"], add_user=True)
    pages = photos["pages"]
    page += 1
    time.sleep(SLEEP_TIME) # ensures doesn't exceed the 1 request per second limit
  except:
    print("Error occured whilst getting recent photos, moving onto hottest tags")
    break

# Search over the hottest tags for photos
print("Searching over hottest tags... ", queries_made)
hot_tags = flickr.tags.getHotList(count=200)["hottags"]["tag"]
time.sleep(SLEEP_TIME) # ensures doesn't exceed the 1 request per second limit
queries_made += 1
for tag in hot_tags:
  tag = tag["_content"]
  page = 1
  pages = 1
  while(page <= pages and page <= MAX_PAGES and keep_running()):
    try:
      photos = flickr.photos.search(tags=tag, tag_mode="all",extras=EXTRAS, page=page, per_page=500)["photos"]
      queries_made += 1
      insert_into_db(photos["photo"], add_user=True)
      pages = photos["pages"]
      page += 1
      time.sleep(SLEEP_TIME) # ensures doesn't exceed the 1 request per second limit
    except:
      print("Error occured whilst getting hottest tag: ", tag, ". Moving onto next tag")
      break


# For each user in the queue, get all users public photos
print("Processing users in queue... ", queries_made)
while(not users_to_process.empty() and keep_running()):
  user = users_to_process.get()
  page = 1
  pages = 1
  while(page <= pages and pages <= MAX_PAGES and keep_running()):
    try:
      photos = flickr.people.getPublicPhotos(user_id=user, extras=EXTRAS, per_page=500, page=page)["photos"]
      queries_made += 1
      insert_into_db(photos["photo"])
      pages = photos["pages"]
      page += 1
      time.sleep(SLEEP_TIME) # ensures doesn't exceed the 1 request per second limit
    except:
      print("Error occured whilst processing user: ", user, ". Moving onto next user")
      break


print("Queries made: ", queries_made)
print("Start time: ", start_time)
print("End time: ", end_time)

