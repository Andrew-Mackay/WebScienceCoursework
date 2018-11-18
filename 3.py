# Tweet clustering and Geo assignment

import config
from pymongo import MongoClient
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.externals import joblib

LOAD_KMEANS = False
EVALUATION = False
SAVE_GRAPH = True
# collection = "enhanced_crawler_1b"
collection = "twitter_sample"

client = MongoClient()
db = client.twitterdb

tweet_text = []
tweet_mongo_id = []
place = []
take_half_helper = False # used for taking 50% of geo data in evaluation
original_geo_data = {} # used for later evaluation
for tweet in db[collection].find({}, {"text":1, "_id":1, "place":1}):
  tweet_text.append(tweet["text"])
  tweet_mongo_id.append(tweet["_id"])
  tweet_place = tweet["place"]
  if EVALUATION:
    if tweet_place is not None:
      if take_half_helper:
        original_geo_data[tweet["_id"]] = tweet_place["name"]
        tweet_place = None

      take_half_helper = not take_half_helper
  place.append(tweet_place)

#define vectorizer parameters
tfidf_vectorizer = TfidfVectorizer() # stop_words="english" provided a 1% increase to classification

tfidf_matrix = tfidf_vectorizer.fit_transform(tweet_text) #fit the vectorizer to tweet text

num_clusters = 20

if LOAD_KMEANS:
  km = joblib.load('k_means_model.pkl')

else: 
  km = KMeans(n_clusters=num_clusters)
  km.fit(tfidf_matrix)
  joblib.dump(km,  'k_means_model.pkl')

clusters = km.labels_.tolist()

tweets = { 'mongo_id': tweet_mongo_id, 'tweet_text': tweet_text, 'cluster': clusters, 'place':place }
df = pd.DataFrame(tweets, index = [clusters] , columns = ['mongo_id', 'cluster', 'tweet_text', 'place'])

group_counts = df['cluster'].value_counts().sort_index()

def extract_place(row):
  return row["name"]

def compute_new_location(row, new_location):
  if row is not None:
    return row["name"]
  return new_location

geo_counts = [] # number of tweets geo-tagged per group
gained_location = [] # number of tweets in the group that are assigned a new location
profile_location_counts = [] # number of tweets whose user has set their profile location
voted_location = [] # the majority location for the given group

for group in range(num_clusters):
  group_rows = df.loc[df['cluster'] == group]
  ids = group_rows["mongo_id"].values.tolist()
  geo_counts.append(group_rows["place"].count())
  non_geo = group_rows["place"].isna().sum()

  profile_location_counts.append(
    db[collection].count_documents(
      {"_id": {"$in": ids},
       "user.location": {"$ne" : None}
       }))

  filtered_out_null = group_rows["place"][group_rows["place"].notna()]
  location_vote = None
  if len(filtered_out_null) != 0:
    places = filtered_out_null.apply(lambda row: extract_place (row))
    location_vote = places.mode()[0]
    gained_location.append(non_geo)
    del places

  else:
    gained_location.append(0)
  del filtered_out_null
  del group_rows
  voted_location.append(location_vote)
  df.loc[df.cluster == group, 'place'] = df.loc[df.cluster == group].place.apply(lambda row: compute_new_location(row, location_vote))

groups_with_no_geo_location = []
for i in range(len(gained_location)):
  if gained_location[i] == 0:
    groups_with_no_geo_location.append(i)

print("Groups with no geo location:", groups_with_no_geo_location)

total_non_geo = df.place.isna().sum()
print("Total tweets not geo assigned:", total_non_geo)

bar_width = 0.2
plt.figure()
plt.bar(np.arange(num_clusters)-bar_width, group_counts, label="Total Tweets", width=-bar_width, align="edge")
plt.bar(np.arange(len(geo_counts)), geo_counts, label="Geo-Tagged", width=-bar_width, align="edge")
plt.bar(np.arange(len(profile_location_counts)), profile_location_counts, label="Profile Location", width=bar_width, align="edge")
plt.bar(np.arange(len(gained_location))+bar_width, gained_location, label="Assigned New Location", width=bar_width, align="edge")
plt.legend()
plt.xticks(range(num_clusters))
plt.title("Tweet Cluster and Geo-location assignment")
plt.xlabel("Cluster")
plt.ylabel("Number of Tweets")
plt.tight_layout()
if SAVE_GRAPH:
  plt.savefig(os.getcwd() + "/tweet_cluster_analysis.svg" , format='svg', dpi=1200)
plt.show()


if EVALUATION:
  total = 0
  correct = 0
  for id, actual_location in original_geo_data.items():
    assigned_location = df[df["mongo_id"] == id].place.item()
    if actual_location == assigned_location:
      correct += 1
    total += 1
  print("Correct:", correct, " Total:", total, " Percentage: ", (correct/total)*100)