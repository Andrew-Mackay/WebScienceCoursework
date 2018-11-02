import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
import os

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
                        { "$mod": [{ "$minute": "$created_at"}, 2] }
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
                        { "$mod": [{ "$minute": "$created_at"}, 2] }
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
                        { "$mod": [{ "$minute": "$created_at"}, 2] }
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
                        { "$mod": [{ "$minute": "$created_at"}, 2] }
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
    plt.xlabel("Duration of 10 Minutes")
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
    plt.bar(range(len(heights_grouped)), heights_grouped, align='edge')
    plt.bar(range(len(heights_duplicates)), heights_duplicates, align='edge')
    plt.xticks(range(len(x_labels)), x_labels)
    plt.xlabel("Duration of 10 Minutes")
    plt.ylabel("Number of Tweets")
    plt.title("Collection: " + collection_name)
    if save:
        plt.savefig(os.getcwd() + "/barcharts/" + collection_name + "_duplicates" + '.svg' , format='svg', dpi=1200)
    plt.show()

def plot_retweets_quotes_histogram(start_time, end_time, collection_name, save=True):
    grouped_tweets = get_tweets_grouped_by_time(start_time, end_time, collection_name)
    grouped_retweets = get_retweeted_grouped_by_time(start_time, end_time, collection_name)
    grouped_quotes = get_quoted_grouped_by_time(start_time, end_time, collection_name)
    heights_grouped = []
    x_labels = [x for x in range(0, 70, 10)]
    for group in grouped_tweets:
        print(group)
        heights_grouped.append(group["total"])

    heights_retweets = []
    for group in grouped_retweets:
        heights_retweets.append(group["total"])

    heights_quotes = []
    for group in grouped_quotes:
        heights_quotes.append(group["total"])

    plt.figure()
    plt.bar(range(len(heights_grouped)), heights_grouped, align='edge')
    plt.bar(range(len(heights_retweets)), heights_retweets, align='edge')
    plt.bar(range(len(heights_quotes)), heights_quotes, align='edge')
    plt.xticks(range(len(x_labels)), x_labels)
    plt.xlabel("Duration of 10 Minutes")
    plt.ylabel("Number of Tweets")
    plt.title("Collection: " + collection_name)
    if save:
        plt.savefig(os.getcwd() + "/barcharts/" + collection_name + "_rt_qt" + '.svg' , format='svg', dpi=1200)
    plt.show()


if __name__ == '__main__':
    collections = ["basic_crawler_1a", "enhanced_crawler_1b", "geo_tagged_1c"]
    start = datetime(2018, 11, 2, 19, 0)
    end = datetime(2018, 11, 2, 19, 60)
    for collection in collections:
        plot_basic_histogram(start, end, collection)
        plot_duplicate_histogram(start, end, collection)
        plot_retweets_quotes_histogram(start, end, collection)




