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

---

| File        | Description           | Related Task  |
| ------------- |:-------------:| -----:|
| 1a.py                      | Basic Crawler Script for Task 1a         | 1a |
| 1b.py                      | Enhanced Crawler Script for Task 1b      | 1b |
| 1c.py                      | Glasgow Geo-tagged Crawler Script for Task 1c      | 1c |
| 2.py                       | Performs numerical analysis of the collections from 1a, b and c | 2 |
| 2_histograms.py            | Generates histograms based on the collections from 1a, b and c      |   2 |
| 3.py                       | Performs clustering, generates graphs and optional evaluation based on task 3           |  3 |
| 4_crawler_flickr.py        | right-aligned | 4 |
| 4_analytics.py             | centered      | 4 |
| 4_graphs.py                | are neat      | 4 |
| config.py                  | Contains API keys for Twitter API | 1 |
| config_flickr.py           | Contains API keys for Flickr API      | 4 |
| /barcharts/                | Contains all histograms as .svg files generated from 2_histograms.py      |    2 |
| k_means_model.pkl          | Contains the k-means python object generated from 3.py to reduce computation time when re-running      |    3 |
| hour_flickr.svg            | Graph produced by 4_graphs.py      |    4 |
| year_flickr.svg            | Graph produced by 4_graphs.py      |    4 |
| tweet_cluster_analysis.svg | Graph produced by 3.py      |    3 |