import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
import os


def bar_chart(grouped_items, title, save=False):
    heights = []
    for group in grouped_items:
        heights.append(group["total"])

    plt.bar(range(len(heights)), heights)
    # plt.xticks(range(len(labels)), labels)
    plt.xlabel("Duration of 10 Minutes")
    plt.ylabel("Number of Tweets")
    plt.title(title)
    file_name = title.split(':')[1][1:]
    if save:
        plt.savefig(os.getcwd() + "/" + file_name + '.svg' , format='svg', dpi=1200)
    plt.show()


def plot_histogram(start_time, end_time, collection_name, title):
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
    
    bar_chart(grouped_by_time, "Collection: " + collection_name, save=True)

start = datetime(2018, 11, 2, 19, 0)
end = datetime(2018, 11, 2, 19, 30)
plot_histogram(start,end,"geo_tagged_1c", "foo")