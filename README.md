LucidWorks Search Financial Demo
==================

Simple Financial Demo for LWS that indexes S&amp;P 500 company info, historical stock prices and Twitter feeds

# Pre-requisites

* Python
* Python json lib (pip install json)
* Pysolr (pip install pysolr)
* Flask (pip install flask)
* LWS 2.6 (www.lucidworks.com/download/) and it's system requirements
* Twitter API authorization (see http://docs.lucidworks.com/display/lweug/Twitter+Stream+Data+Sources and http://dev.twitter.com)
 * You will need your access key, consumer key and related tokens

# Caveats
	Only tested on OS X

# Getting Started

1. Install LWS 2.6 and wait for it to start
2. Clone this project: git clone git@github.com:LucidWorks/lws-financial-demo.git
3. cd src/main/python
4. python setup.py -n setup -a TWITTER_ACCESS_TOKEN -c TWITTER_CONSUMER_KEY -s TWITTER_CONSUMER_SECRET -t TWITTER_ACCESS_TOKEN_SECRET -p ../../../data/sp500List-30.txt -A -l Finance --data_dir ../../../data
 1. This will setup collections, fields and data for the companies in the file sp500List-30.txt
 2. The company file list should be comma-separated list of the form: Symbol,Company,Industry,City,State
5. python python.py
5. Browse to http://localhost:5000/