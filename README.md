# Lucidworks Fusion Financial Services Demo

This demo is designed to showcase Fusion's <FILL ME IN>.

# Help on this Demo

Help on this Demo is available in Slack in the #finance-demo channel.

# Prerequisites

* Your system should have a minimum free memory of 8-12 GB with a 64-bit processor.
* Enough free disk space to support the writing of index files etc.
* JDK8
* Node/NPM (if you want to add new node modules)
* The zip/unzip utility
* A valid Fusion license file, probably stored in your home directory
* Fusion 4.1.1
* You must be running Fusion's `webapps` service
* Maven
* External web access to Yahoo Finance
* External web access to the IEX API.  Validate that `https://api.iextrading.com/1.0/stock/AAPL/chart` returns historical prices for Apple.
* A Google Maps API key that you put in `app/src/main/resources/conf/app-config-private.conf`, with contents `googleMapsKey: <YOUR API KEY>`.


# Setup


## Clone the fusion-financial-demo repo


  `git clone git@github.com:lucidworks/fusion-financial-demo.git`


## One Time Setup Instructions

* Check that you have https://lucidworks.slack.com/files/U92QXC46S/F9QSN33PG/settings.xml in ~/.m2/settings.xml


## Installation

### Setup myenv.sh

   If you're using a default Fusion 4.x setup, then you can skip this step and pass the path to Fusion (e.g. `/opt/fusion/4.1.1`) to install.sh, which will create a myenv.sh script with the default settings.

   However, if you're using a customized Fusion installation, or are not using the default password, etc, then `cp myenv.sh.tmpl myenv.sh` and then edit `./myenv.sh` to verify all env vars are correct for your environment.

### Run

  1. Run `./install.sh`
  1. Run `./redeploy-data.sh`
  1. Browse to http://localhost:8764/ for the Fusion Admin UI
  1. Go to the `Datasources` and run all.  Let the `yahoo-news` datasource run for a long time.  The `sp500` and `sp500-historical` datasources take 1-2 minutes, and the rest are quick.
  1. Browse to http://localhost:8780/Finance/login/ for the end user UI

# Application Overview

There are three personas supported in this app:

1. Portfolio Manager (users `Chloe` and `Lawson`).  Manages investment strategy portfolios.  Differentiators: portfolio holdings view
2. Sellside Analyst (users `Geoffrey` and `Frank`).  Covers companies (writes research, issues guidance and earnings estimates).  Similar to PM, but no notion of portfolios with weighted holdings.
2. Financial Advisor (users `Robert` and `Cynthia`).  Covers client relationship, aids in asset allocation / product decisions.  Has more client-centric views available, e.g., a `Clients` tab that allows them to view clients and their accounts.

# Development

Most demo development should either be on the Application itself in Fusion (either via the UI or the API)
or in the Appkit UI, both of which are covered below.

## Updating the UI

Develop the webapp locally:

1. `cd app`
1. `mvn jetty:run`

And then redeploy as a Fusion webapp:

1. Run `./redeploy.sh`


## Updating the Application

1. Make your changes in the Admin UI or via the APIs or by directly editing the `objects.json` file`.
1. ALL CHANGES TO THE BACKEND APPLICATION MUST BE EXPORTED AND CHECKED IN
1. To Export, run `./export.sh` and then review and commit/push to github
1. You probably want to coordinate with whomever else is working on this application, as with other code, if you are both working on the same area, you will get conflicts.

If you wish to redeploy the backend application, run:

1. `./clean.sh` -- note, this will delete the application and data (it will first export it to `/tmp`)
1. `./install.sh` (same as above)

## Working with Data

This app relies on generated data for clients and portolios.  See the Python scripts in `/scripts`.  The scripts will generate these files: `company_buckets.csv` which includes portfolio holdings, `clients.csv`, and `client_accounts.csv`.  The latter two files are used to support the financial advisor persona.

1. If you put the data in `data/Finance`, then it will automatically show up at http://localhost:8780/data/ and
can easily be accessed via a Web data source.
1. If the data is less than 100 MB, you can just check it in.
1. If it is greater than 100 MB, use Nexus or S3 or GDrive.
    1. Be sure to add downloading it to `prerequisites.sh` if it is in Nexus or S3
1. `./redeploy-data.sh` will repackage and redeploy the data
1. Be warned that `clean.sh` will delete any data you've indexed.  There are tricks to avoiding this, but they are involved:
    1. The following steps are unverified:
        1. Shutdown Fusion
        1. Copy the data directories out of Fusion
        1. Restart Fusion
        1. Delete/clean your application
        1. Shutdown Fusion
        1. Copy the data directories back into Fusion
        1. Restart Fusion
    1. NOTE: This assumes your application hasn't changed the way it processes the data for indexing.

### Parquet file dumping and loading

Sometimes it is more efficient to load and dump data from Parquet (https://parquet.apache.org/) files.  For instance, if you want to fairly
quickly dump out all the records of an index to parquet, you can use the `dump_parquet.sh` script to do so and then
the `load_parquet.sh` to load it back in.  Before running them, however, be sure to edit the underlying Scala files (dump_solr_to_parquet.scala and load_parquet_data.scala)
to properly point at the collections you want to dump/load.

##Troubleshooting


#### Mismatched Fusion Versions

The `setup/app/objects.json` is tied, more or less, to a specific version of Fusion.  If `install.sh` fails on the install and says something about mismatched versions, you may need to change this value.

#### Application or UI is already installed

Run `clean.sh` first then re-install.
