# LSH

import config
from pymongo import MongoClient
from lshash.lshash import LSHash
from datasketch import MinHash, MinHashLSH
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import numpy as np
import pandas as pd
import nltk
from sklearn.cluster import KMeans
from sklearn.externals import joblib

LOAD_KMEANS = True

client = MongoClient()
db = client.twitterdb
tweet_text = []
tweet_mongo_id = []
for tweet in db.enhanced_crawler_1b.find({}, {"text":1, "_id":1}):
  tweet_text.append(tweet["text"])
  tweet_mongo_id.append(tweet["_id"])


#define vectorizer parameters
tfidf_vectorizer = TfidfVectorizer()

tfidf_matrix = tfidf_vectorizer.fit_transform(tweet_text) #fit the vectorizer to tweet text

print(tfidf_matrix.shape)
num_clusters = 20

if LOAD_KMEANS:
  km = joblib.load('tweet_cluster.pkl')

else: 
  km = KMeans(n_clusters=num_clusters)
  km.fit(tfidf_matrix)
  joblib.dump(km,  'tweet_cluster.pkl')

clusters = km.labels_.tolist()

tweets = { 'mongo_id': tweet_mongo_id, 'tweet_text': tweet_text, 'cluster': clusters }
frame = pd.DataFrame(tweets, index = [clusters] , columns = ['mongo_id', 'cluster', 'tweet_text'])

group_counts = frame['cluster'].value_counts().sort_index()


bar_width = 0.2
plt.bar(np.arange(num_clusters)-bar_width, group_counts, label="Total Tweets", width=bar_width)
plt.xticks(range(num_clusters))
geo_counts = []
profile_location_counts = []
for group in range(num_clusters):
  ids = frame.loc[frame['cluster'] == group]["mongo_id"].values.tolist()
  geo_counts.append(db.enhanced_crawler_1b.count_documents({"_id": {"$in": ids}, "place": {"$ne" : None}}))
  profile_location_counts.append(
    db.enhanced_crawler_1b.count_documents(
      {"_id": {"$in": ids},
       "user.location": {"$ne" : None}
       }))

print(geo_counts)
print(profile_location_counts)
plt.bar(np.arange(len(geo_counts))+bar_width, geo_counts, label="Geo-Tagged", width=bar_width)
plt.bar(np.arange(len(profile_location_counts)), profile_location_counts, label="Profile Location", width=bar_width)
plt.legend()
plt.savefig(os.getcwd() + "/kmeanstest.svg" , format='svg', dpi=1200)
plt.show()
