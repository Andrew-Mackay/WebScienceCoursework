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

LOAD_KMEANS = False

client = MongoClient()
db = client.twitterdb
tweet_text = []
tweet_mongo_id = []
for tweet in db.basic_crawler_1a.find({}, {"text":1, "_id":1}):
  tweet_text.append(tweet["text"])
  tweet_mongo_id.append(tweet["_id"])


#define vectorizer parameters
tfidf_vectorizer = TfidfVectorizer()

tfidf_matrix = tfidf_vectorizer.fit_transform(tweet_text) #fit the vectorizer to tweet text

print(tfidf_matrix.shape)

if LOAD_KMEANS:
  km = joblib.load('tweet_cluster.pkl')

else: 
  num_clusters = 10
  km = KMeans(n_clusters=num_clusters)
  km.fit(tfidf_matrix)
  joblib.dump(km,  'tweet_cluster.pkl')

clusters = km.labels_.tolist()

tweets = { 'mongo_id': tweet_mongo_id, 'tweet_text': tweet_text, 'cluster': clusters }
frame = pd.DataFrame(tweets, index = [clusters] , columns = ['mongo_id', 'cluster'])

group_counts = frame['cluster'].value_counts()
print(group_counts)
print(type(group_counts))

group_counts.plot.bar()
plt.savefig(os.getcwd() + "/kmeanstest.svg" , format='svg', dpi=1200)
plt.show()