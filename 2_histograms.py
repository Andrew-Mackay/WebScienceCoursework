import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import os

collections = {
    "basic_crawler_1a": {
        "start_time":datetime(2018, 11, 14, 11, 0),
        "end_time":datetime(2018, 11, 14, 12, 0)
        },
    "enhanced_crawler_1b": {
        "start_time":datetime(2018, 11, 14, 12, 0),
        "end_time":datetime(2018, 11, 14, 13, 0)
        },
    "geo_tagged_1c": {
        "start_time":datetime(2018, 11, 14, 13, 0),
        "end_time":datetime(2018, 11, 14, 14, 0)
        }
    }

def get_tweets_grouped_by_time(start_time, end_time, collection_name):
    client = MongoClient()
    db = client.twitterdb
    collection = db[collection_name]
    grouped_by_time = collection.aggregate([
        {
            "$match": {
                "created_at": {
                    "$gte": start_time,
                    "$lt": end_time
                }
            }
        },
        {
            '$group': {
                "_id": { 
                    "y": {'$year': '$created_at'},
                    "m": {'$month': '$created_at'},
                    "d": {'$dayOfMonth': '$created_at'},
                    "h": {'$hour': '$created_at'},
                    "interval": {
                        "$subtract": [ 
                        { "$minute": "$created_at" },
                        { "$mod": [{ "$minute": "$created_at"}, 10] }
                        ]
                    }
                },
                "total": {'$sum': 1}
            }
        }
    ])
    return grouped_by_time

def get_duplicates_grouped_by_time(start_time, end_time, collection_name):
    client = MongoClient()
    db = client.twitterdb
    duplicate_ids = []
    duplicates = db[collection_name].aggregate([
        {            
            "$match": {
                "created_at": {
                    "$gte": start_time,
                    "$lt": end_time
                }
            }
        },
        {
            "$group": {
                "_id": {"id": "$id"},
                "uniqueIds": {"$addToSet": "$_id"},
                "count": {"$sum": 1} 
            } 
        }, 
        {
            "$match": { 
                "count": {"$gte": 2 } 
            }
        }
    ])
    # get mongo ids for all duplicate tweets
    for duplicate in duplicates:
        for id in duplicate['uniqueIds']:
            duplicate_ids.append(id)
    grouped_by_time = db[collection_name].aggregate([
        {
            "$match": {
                "_id": {
                    "$in": duplicate_ids
                    }
            }
        },
        {
            '$group': {
                "_id": { 
                    "y": {'$year': '$created_at'},
                    "m": {'$month': '$created_at'},
                    "d": {'$dayOfMonth': '$created_at'},
                    "h": {'$hour': '$created_at'},
                    "interval": {
                        "$subtract": [ 
                        { "$minute": "$created_at" },
                        { "$mod": [{ "$minute": "$created_at"}, 10] }
                        ]
                    }
                },
                "total": {'$sum': 1}
            }
        }
    ])
    return grouped_by_time

def get_retweeted_grouped_by_time(start_time, end_time, collection_name):
    client = MongoClient()
    db = client.twitterdb
    collection = db[collection_name]
    grouped_by_time = collection.aggregate([
        {
            "$match": {
                "$and": [{
                    "created_at": {
                        "$gte": start_time,
                        "$lt": end_time
                    },
                    "retweeted_status": {
                        "$exists": True
                    }
                }]
            }
        },
        {
            '$group': {
                "_id": { 
                    "y": {'$year': '$created_at'},
                    "m": {'$month': '$created_at'},
                    "d": {'$dayOfMonth': '$created_at'},
                    "h": {'$hour': '$created_at'},
                    "interval": {
                        "$subtract": [ 
                        { "$minute": "$created_at" },
                        { "$mod": [{ "$minute": "$created_at"}, 10] }
                        ]
                    }
                },
                "total": {'$sum': 1}
            }
        }
    ])
    return grouped_by_time

def get_quoted_grouped_by_time(start_time, end_time, collection_name):
    client = MongoClient()
    db = client.twitterdb
    collection = db[collection_name]
    grouped_by_time = collection.aggregate([
        {
            "$match": {
                "$and": [{
                    "created_at": {
                        "$gte": start_time,
                        "$lt": end_time
                    },
                    "is_quote_status": True
                }]
            }
        },
        {
            '$group': {
                "_id": { 
                    "y": {'$year': '$created_at'},
                    "m": {'$month': '$created_at'},
                    "d": {'$dayOfMonth': '$created_at'},
                    "h": {'$hour': '$created_at'},
                    "interval": {
                        "$subtract": [ 
                        { "$minute": "$created_at" },
                        { "$mod": [{ "$minute": "$created_at"}, 10] }
                        ]
                    }
                },
                "total": {'$sum': 1}
            }
        }
    ])
    return grouped_by_time

def plot_basic_histogram(start_time, end_time, collection_name, save=True):
    grouped_tweets = get_tweets_grouped_by_time(start_time, end_time, collection_name)
    heights_grouped = []
    x_labels = range(0, 70, 10)
    for group in grouped_tweets:
        heights_grouped.append(group["total"])

    plt.figure()
    plt.bar(range(len(heights_grouped)), heights_grouped, align='edge')
    plt.xticks(range(len(x_labels)), x_labels)
    plt.xlabel("Elapsed Time (Minutes)")
    plt.ylabel("Number of Tweets")
    plt.title("Collection: " + collection_name)
    if save:
        plt.savefig(os.getcwd() + "/barcharts/" + collection_name + "_basic" + '.svg' , format='svg', dpi=1200)
    plt.show()

def plot_duplicate_histogram(start_time, end_time, collection_name, save=True):
    grouped_tweets = get_tweets_grouped_by_time(start_time, end_time, collection_name)
    duplicate_tweets = get_duplicates_grouped_by_time(start_time, end_time, collection_name)
    heights_grouped = []
    x_labels = range(0, 70, 10)
    for group in grouped_tweets:
        heights_grouped.append(group["total"])

    heights_duplicates = []
    for group in duplicate_tweets:
        heights_duplicates.append(group["total"])

    plt.figure()
    plt.bar(range(len(heights_grouped)), heights_grouped, align='edge', label="Total Tweets")
    plt.bar(range(len(heights_duplicates)), heights_duplicates, align='edge', label="Duplicates")
    plt.xticks(range(len(x_labels)), x_labels)
    plt.xlabel("Elapsed Time (Minutes)")
    plt.ylabel("Number of Tweets")
    plt.title("Collection: " + collection_name)
    plt.legend()
    if save:
        plt.savefig(os.getcwd() + "/barcharts/" + collection_name + "_duplicates" + '.svg' , format='svg', dpi=1200)
    plt.show()

def plot_retweets_quotes_histogram(start_time, end_time, collection_name, save=True):
    grouped_tweets = get_tweets_grouped_by_time(start_time, end_time, collection_name)
    grouped_retweets = get_retweeted_grouped_by_time(start_time, end_time, collection_name)
    grouped_quotes = get_quoted_grouped_by_time(start_time, end_time, collection_name)
    heights_grouped = []
    interval_tweets = []
    interval_retweets = []
    interval_quoted_tweets = []
    x_labels = [x for x in range(0, 70, 10)]
    for group in grouped_tweets:
        heights_grouped.append(group["total"])
        interval_tweets.append(group["_id"]["interval"]/10)

    heights_retweets = []
    for group in grouped_retweets:
        heights_retweets.append(group["total"])
        interval_retweets.append(group["_id"]["interval"]/10)

    heights_quotes = []
    for group in grouped_quotes:
        heights_quotes.append(group["total"])
        interval_quoted_tweets.append(group["_id"]["interval"]/10)


    plt.figure()
    if len(interval_tweets) > 0:
        plt.bar(interval_tweets, heights_grouped, align='edge', label="Total Tweets")
    if len(interval_retweets) > 0:
        plt.bar(interval_retweets, heights_retweets, align='edge', label="Retweets")
    if len(interval_quoted_tweets) > 0:
        plt.bar(interval_quoted_tweets, heights_quotes, align='edge', label="Quotes")
    plt.xticks(range(len(x_labels)), x_labels)
    plt.xlabel("Duration of 10 Minutes")
    plt.ylabel("Number of Tweets")
    plt.title("Collection: " + collection_name)
    plt.legend()
    if save:
        plt.savefig(os.getcwd() + "/barcharts/" + collection_name + "_rt_qt" + '.svg' , format='svg', dpi=1200)
    plt.show()


for collection, time in collections.items():
    plot_basic_histogram(time["start_time"], time["end_time"], collection)
    plot_duplicate_histogram(time["start_time"], time["end_time"], collection)
    plot_retweets_quotes_histogram(time["start_time"], time["end_time"], collection)




