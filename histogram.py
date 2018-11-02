import matplotlib.pyplot as plt
from pymongo import MongoClient

def plot_histogram(start_time, end_time, collection_name, title):
    client = MongoClient()
    db = client.twitterdb
    collection = db[collection_name]
    x = collection.aggregate([
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


plot_histogram(1,2,"basic_crawler_1a", "foo")