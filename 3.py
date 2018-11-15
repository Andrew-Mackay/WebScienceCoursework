# LSH

import config
from pymongo import MongoClient
from lshash.lshash import LSHash
from datasketch import MinHash, MinHashLSH
import matplotlib.pyplot as plt
import os
client = MongoClient()
db = client.twitterdb


lsh = LSHash(5,256)

for text in db.basic_crawler_1a.find({}, {"text":1, "_id":0}):
  m = MinHash(num_perm=256)
  m.update(text["text"].encode('utf8'))
  lsh.index(m.digest())

hash_table = lsh.hash_tables[0]
x = hash_table.keys()
y = []
for table in x:
  y.append(len(hash_table.get_val(table)))

print(x)
print(y)
plt.figure()
plt.bar(x, y, align='edge')
plt.xticks(rotation=90)
# plt.xticks(range(len(x_labels)), x_labels)
# plt.xlabel("Elapsed Time (Minutes)")
# plt.ylabel("Number of Tweets")
plt.title("LSH")
plt.savefig(os.getcwd() + "/lsh.svg" , format='svg', dpi=1200)
plt.show()
  # print(m.digest().shape)
  # break
# lsh.index([1,2,3,4,5,6,7,8])
# lsh.index([2,3,4,5,6,7,8,9])
# lsh.index([10,12,99,1,5,31,2,3])

# lsh = LSHash(6,1)
# lsh.index(4)
# print(lsh.query([1,2,3,4,5,6,7,7]))

# lsh = MinHashLSH(threshold-0.5, num_perm=128)
# vectorizer = TfidfVectorizer()
# corpus = []
# for text in db.basic_crawler_1a.find({}, {"text":1, "_id":0}):
#   corpus.append(text["text"])

# X = vectorizer.fit_transform(corpus)
# print("done")
# print(X.shape)
# print(X[0])
# m = MinHash(num_perm=256)
# for text in corpus:
#   m.update(text.encode('utf8'))

# print(m.digest())
#   print(text["text"])
#     m1 = MinHash(num_perm=256)
#     for word in tweet["text"].split():
#       print(word)
#       m1.update(word.encode('utf8'))
#       print(m1)

    #  lsh.index(tweet)

