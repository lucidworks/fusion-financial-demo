#!/usr/bin/env bash

source ./bash-header.sh

source "$DEMO_HOME/myenv.sh"

OPTIND=1
no_download=0

while getopts "hdc" opt; do
    case "$opt" in
    h|\?)
        echo "do something else, no help here"
        exit 0
        ;;
    d)  no_download=1
        ;;
    c)  no_crawl=1
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

echo "No download=$no_download, No Crawl=$no_crawl, Leftovers: $@"

cd "$DEMO_HOME/target"

if [ "$no_download" -eq 0 ]; then
  # Here is an example of downloading a connector
  #echo "Downloading Connector JARs"
  #echo ""
  #curl https://download.lucidworks.com/fusion-4.1.0/lucidworks.sharepoint-4.1.0.zip > lucidworks.sharepoint.4.1.0.zip

  # Here is an example of downloading a large data set

  cd "$DEMO_HOME/data/"
  mkdir "$DEMO_HOME/data/$FUSION_APPLICATION_NAME"
  #Replace this next line with your data download
  touch "$DEMO_HOME/data/$FUSION_APPLICATION_NAME/.gitkeep"
  #mkdir "all_data"
  #cd all_data
  #echo "Downloading ECommerce Datasets.  This will take some time."
  #echo -n Your Lucidworks LDAP username:
  #read -s username
  #echo ""
  #echo -n Your Lucidworks LDAP Password:
  #read -s password
  #echo ""
  #echo "Downloading using username: "  $username
  #curl -u "$username":"$password" https://ci-nexus.lucidworks.com/service/local/repositories/datasets/content/com/lucid/data/ecommerce-demo/ecomm_data-1.1.tar.gz/1.1/ecomm_data-1.1.tar.gz-1.1.gz > ecomm_data.tar.gz
  #tar -xf ecomm_data.tar.gz
fi

# Finish off the install of connectors
#echo "Installing Connector JARs"
#echo ""
#curl -X PUT -H 'Content-type: application/zip' --data-binary "@./lucidworks.sharepoint.$FUSION_VERSION.zip" "$FUSION_API/blobs/lucidworks.sharepoint.$FUSION_VERSION.zip?resourceType=plugin:connector"

