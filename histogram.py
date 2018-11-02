import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime


def plot_histogram(start_time, end_time, collection_name, title):
    client = MongoClient()
    db = client.twitterdb
    collection = db[collection_name]
    # within_time_slot = collection.find({
    #     "created_at": {
    #         "$gte": start_time,
    #         "lt": end_time
    #     }
    # })
    x = collection.aggregate([
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
                    "h": {'$hour': '$created_at'}
                },
                "total": {'$sum': 1}
            }
        }
    ])
    
    for y in x:
        print(y)

start = datetime(2018, 11, 2, 19, 0)
end = datetime(2018, 11, 2, 19, 30)
plot_histogram(start,end,"geo_tagged_1c", "foo")