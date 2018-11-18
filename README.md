# WebScience Coursework 2018
---
Author: Andrew Mackay

Matriculation Number: 2192793m

---
## Environment:
This project has been developed using Python version 3.6.6 alongside the environment as specified in the requirements.txt file.
This project also relies on having a MongoDB instance running. Mongo version 2.6.10 was used.

---
## Setup:
First create a new Python environment based on Python 3.6.6.

Next, activate this newly created environment and install the required packages with the command: `pip install -r requirements.txt`

Install and run MongoDB version 2.6.10 (later versions should work but have not been tested).
The command to run the mongo is: `sudo service mongodb start`

The files config.example.py and config_flickr.example.py contain the structure for the config files.
Run `mv config.example.py config.py` and then `mv config_flickr.example.py config_flickr.py`.
Next, open the files and fill in your API keys. They should be in string format.

## File Descriptions

| File        | Description           | Related Task  |
| ------------- |:-------------| :-----|
| 1a.py                      | Basic Crawler Script for Task 1a         | 1a |
| 1b.py                      | Enhanced Crawler Script for Task 1b      | 1b |
| 1c.py                      | Glasgow Geo-tagged Crawler Script for Task 1c      | 1c |
| 2.py                       | Performs numerical analysis of the collections from 1a, b and c | 2 |
| 2_histograms.py            | Generates histograms based on the collections from 1a, b and c      |   2 |
| 3.py                       | Performs clustering, generates graphs and optional evaluation based on task 3           |  3 |
| 4_crawler_flickr.py        | Flickr Crawler Script for Task 4 | 4 |
| 4_analytics.py             | Performs numerical analysis of the collection produced from 4_crawler_flickr.py      | 4 |
| 4_graphs.py                | Generates graphical analysis of the collection produced from 4_crawler_flickr.py     | 4 |
| config.py                  | Contains API keys for Twitter API | 1 |
| config_flickr.py           | Contains API keys for Flickr API      | 4 |
| /barcharts/                | Contains all histograms as .svg files generated from 2_histograms.py      |    2 |
| k_means_model.pkl          | Contains the k-means python object generated from 3.py to reduce computation time when re-running      |    3 |
| hour_flickr.svg            | Graph produced by 4_graphs.py      |    4 |
| year_flickr.svg            | Graph produced by 4_graphs.py      |    4 |
| tweet_cluster_analysis.svg | Graph produced by 3.py      |    3 |

## Basic Instructions for Running Crawlers and Performing Analytics on Sample Data:
### Running Crawlers:
| Crawler Name        | Instruction           | Collection Name  |
| ------------- |:-------------| :-----|
| Basic Crawler               | `python 1a.py`     | basic_crawler_1a |
| Enhanced Crawler            | `python 1b.py`     | enhanced_crawler_1b |
| Geo-tagged Glasgow Crawler  |  `python 1c.py `      | geo_tagged_1c |
| Flickr Crawler              | `python 4_crawler_flickr.py` | flickr_crawler_4 |

### Running Analytics:
| Analytic       | Instruction           | Graph Location  |
| ------------- |:-------------| :-----|
|  *DO NOT RUN*  Script used for generating total counts for the report. Provides Counts/Analytics for all original three collections  | ~~`python 2.py`~~     | N/A |
| Histograms on sample Twitter data (collection: sample_twitter)            | `python 2_histograms.py`     | `/barcharts/sample_twitter(_basic, _duplicate, _rt_qt).svg` |
| Counts/Analytics on sample Flickr data (collection: sample_flickr)  |  `python 4_analytics.py `      | N/A |
| Graphs for sample Flickr data (collection: sample_flickr)             | `python 4_graphs` | `/year_flickr.svg`, `/hour_flickr.svg` |

### Running Clustering and Evaluation (Task 3):
Run `python 3.py`. The graph will be saved at `tweet_cluster_analysis.svg`.
---

## Advanced Instructions for Using the Software on New Data:

### 1a.py:
Open the file and on line 14 set the name of the desired mongodb collection. The default is "basic_crawler_1a".
The run time of the program can also be adjusted by modifying line 13. The default is 60 minutes.

Once you have set these variables run the program with `python 1a.py`

### 1b.py:
Open the file and on line 17 set the name of the desired mongodb collection. The default is "enhanced_crawler_1b".
The run time of the program can also be adjusted by modifying line 15. The default is 60 minutes.

Once you have set these variables run the program with `python 1b.py`

### 1c.py:
Open the file and on line 20 set the name of the desired mongodb collection. The default is "geo_tagged_1c".
The run time of the program can also be adjusted by modifying line 16. The default is 60 minutes.
Once you have set these variables run the program with `python 1c.py`

### 2.py:
Open the file and on line 8 set the dictionary of dictionaries to be the names of the collections you want to run the analytics on.
For example, to run on collections basic_crawler_1a, enhanced_crawler_1b and  geo_tagged_1c the code would look like: `collections = {"basic_crawler_1a": {}, "enhanced_crawler_1b":{}, "geo_tagged_1c":{}}`
The default will run on the sample data provided (`INSERT CODE HERE`)

Once you have set this variable, run the program with `python 2.py`

### 2_histograms.py:
Open the file and on line 7 modify the names of collections and start/end times to matched desired data.
The default will run on the sample data (`INSERT CODE HERE`). The graphs will be saved in /barcharts/name_of_collection.svg.

An example input would be:
```
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
```
Run the program with `python 2_histograms.py`

### 3.py:
Open the file and on lines 13, 14, 15 and 16 you will find configuration setttings.
On line 13, setting `Load_KMEANS = True` will load precomputed k-means object from a file. This has been set to True by default and the model pre-computed for the sample data provided however if you change the collection on line 16 then this will need to be toggled to False. On line 14 is the toggle whether to run the evaluation method or not. If this is set to True then 50% of the geo-tagged tweets will be set to None and an evaluation performed on the classifiers ability. On line 15 the toggle wether to save the graphs or not is found. The saved graphs can be found at `/tweet_cluster_analysis.svg`. On line 16 is where the name of the collection is specified, by default this is the sample collection.

Example configuration would be:
```
LOAD_KMEANS = True
EVALUATION = True
SAVE_GRAPH = False
collection = "enhanced_crawler_1b"
```
Run the program with `python 3.py`
### 4_crawler_flickr.py:
Open the file and on line 11 you can specifiy the time to run the crawler for. The default is 60 minutes.
On line 12 you can specifiy the collection name, the default is `*TODO*`.

Example configuration:
```
RUN_TIME = 60 
COLLECTION_NAME = "flickr_crawler_4_v2"
```
Run the program with `python 4_crawler_flickr.py`
### 4_analytics.py:
Open the file and on line 9 set the collection name to be the desired collection. By default this is the sample data set.

Run the program with `python 4_analytics.py`
### 4_graphs.py:
Open the file and on line 10 set the collection name to be the desired collection. By default this is the sample data set.
The graphs are saved as `/hour_flickr.svg` and `year_flickr.svg`

Run the program with `python 4_graphs.py`