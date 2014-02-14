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

Getting Started
=================

1. Install LWS 2.6 and wait for it to start
2. Clone this project: git clone git@github.com:LucidWorks/lws-financial-demo.git
3. cd src/main/python
4. python setup.py -n setup -a TWITTER_ACCESS_TOKEN -c TWITTER_CONSUMER_KEY -s TWITTER_CONSUMER_SECRET -t TWITTER_ACCESS_TOKEN_SECRET -p ../../../data/sp500List-30.txt -A -l Finance --data_dir ../../../data
 1. This will setup collections, fields and data for the companies in the file sp500List-30.txt
 2. The company file list should be comma-separated list of the form: Symbol,Company,Industry,City,State
5. python python.py
5. Browse to http://localhost:5000/

Adding Security
=================

If you wish to simulate filtering content and controlling access to the Admin via an LDAP server, you can either hook this demo into your
  own LDAP system or setup one.  For the purposes of the demo, we are going to setup a local LDAP server using <a href="https://opends.java.net">OpenDS</a>, a
  freely available, Java-based LDAP server.  While OpenDS is not actively maintained, it's capabilities are sufficient for demo purposes and local testing.

# Setup

To get started, do the following:

1. Download OpenDS.  For the purposes of the demo, we used version <a href="https://java.net/projects/opends/downloads/download/promoted-builds/2.2.0/OpenDS-2.2.0.zip">2.2</a>
2. Unzip OpenDS and follow the <a href="https://java.net/projects/opends/pages/2_2_InstallationGuide">Installation instructions</a>.  As part of setup, I had the installer automatically populate the server with 50 users.  Alternatively, you can add your own users.
3. Setup LWS with LDAP, per http://docs.lucidworks.com/display/lweug/LDAP+Integration.  I've checked in a sample ldap.yml (named ldap-sample.yml) in the docs directory based off of my local OpenDS setup.
    > NOTE: MAKE SURE YOU HAVE AN ADMIN USER SETUP PER THE INSTRUCTIONS BEFORE TURNING ON LDAP IN LWS OTHERWISE YOU WILL NOT BE ABLE TO LOG IN TO THE ADMIN.
4. Create a Search Filter:
  1. Log in to the LWS UI
  2. Select the Finance Collection
  3. Select the "Access Control" option and add a Filter.  For example:
    > 1. Name: user10
    > 1. Users: user.10   //If using auto generated data from OpenDS
    > 1. Search Filters: symbol:AES  //user.10 may only see info about AES
5. When starting the python application (python python.py from above) you need to pass in your LDAP URI, etc.:
    > 1. python python.py  --ldap ldap://localhost:1389
    > 1. You may optionally pass in the LDAP root user/password too (the defaults are: cn=Directory Manager,cn=Root DNs,cn=config and 'abc':
    > 1. python python.py  --ldap ldap://localhost:1389 --ldap_user cn=Directory Manager,cn=Root DNs,cn=config --ldap_pass foo

# Search Time

1. In the Results tab, in the demo (http://localhost:5000/), when LDAP is enabled, you should see a drop down of users next to the search button.  If you wish to pass in a user's credential, simply select the user from the dropdown, otherwise, select None.
2. If the user selected has an associated Search Filter setup to it, the results will be filtered appropriately.




