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
1. Run the "index-s-and-p" crawler first.  This will index the metadata about the S&P 500 companies AND will create 2 additional crawlers PER company
1. Run the "start-crawlers" crawler, which will kick off all of the newly created crawlers.
1. TODO: In the Fusion Admin UI, run the "start-crawlers" datasource to kick off indexing of the various sources. 
1. TODO: Start up the UI and browse to http://localhost:8080


Developent Notes
=================

1. ```historical-datasource-SAVE.json``` and ```press-release-datasource-SAVE.json``` are convenience files for configuring the REST Stage Entity.  You do not need to do
anything with them as part of setup, but if you want to edit the datasource "templates", edit these first and then copy them into the appropriate REST/RPC Entity stage.
1. Run the ```delete-crawlers``` connector before exporting the configuration, lest all of the intermediary crawler configs are saved.  TODO: maybe we should just do that?

