Lucidworks Fusion Financial Demo
==================

Simple Financial Demo for LWS that indexes S&P 500 company info and historical stock price information.

# Pre-requisites

* Fusion 3.0.1 or later
* A Twigkit development/production license.  See http://twigkit.com 

# Caveats
	Only tested on OS X

Getting Started
=================

1. Install Fusion 3.0.1
1. Clone this project: git clone git@github.com:LucidWorks/fusion-financial-demo.git
1. Import the setup/fusion-config.json file into Fusion.  See https://doc.lucidworks.com/fusion/3.0/REST_API_Reference/Objects-API.html#object-export-and-import
  1. In the Admin UI, you can load up the config under the Devops-Import Menu.
1. Setup the S&P 500 datasource to load up one of the files in data/sp as a "File Upload Datasource".  TODO: MORE DETAILS HERE
1. In the Fusion Admin UI, run the "start-crawlers" datasource to kick off indexing of the various sources. 
1. Start up the UI and browse to http://localhost:8080

