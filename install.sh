#!/usr/bin/env bash

set -x

source ./bash-header.sh

source "$DEMO_HOME/myenv.sh"

cd "$DEMO_HOME"
OPTIND=1
no_build=0
no_crawl=0

while getopts "hbc" opt; do
    case "$opt" in
    h|\?)
        echo "do something else, no help here"
        exit 0
        ;;
    b)  no_build=1
        ;;
    c)  no_crawl=1
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

echo "No Build=$no_build, No Crawl=$no_crawl, Leftovers: $@"

# Build the stuff
if [ "$no_build" -eq 0 ]; then
    mvn clean package

fi

mkdir -p "$DEMO_HOME/app/objects/blobs/webapps"
cp "$DEMO_HOME/app/dist/$FUSION_UI_ARTIFACT_ID.war" "$DEMO_HOME/app/objects/blobs/webapps/$FUSION_UI_ARTIFACT_ID.war"
# TODO: download the data, check if it is there, unzip,
cd "$DEMO_HOME/data"
# https://ci-nexus.lucidworks.com/service/local/repositories/datasets/content/com/lucid/data/bio-it-demo-data.zip/1.0/bio-it-demo-data.zip-1.0.zip
jar -cf ../target/data.war index.html "$FUSION_APPLICATION_NAME"/*.*

cd "$DEMO_HOME/setup"

echo "Installing the Data"
echo ""
curl -H 'Content-type: application/json' -X POST -d "@data_appstudio.json" "$FUSION_API/webapps"
curl -H 'Content-type: application/zip' -X PUT "$FUSION_API/webapps/data/war" --data-binary "@../target/data.war"
sleep 5 # Let the data load

# Example of loading in a large data set
#echo ""
#echo "Linking XML trial data"
#echo ""
#cp "$DEMO_HOME/data/static.xml" "$FUSION_HOME/apps/jetty/webapps/webapps/"
#SED_PATTERN="s|_DEMO_HOME_|$DEMO_HOME|g"
#sed -i.bak "$SED_PATTERN" "$FUSION_HOME/apps/jetty/webapps/webapps/static.xml"
cd "$DEMO_HOME/app/objects"
zip -q -r $FUSION_APPLICATION_NAME.zip objects.json blobs/* configsets/*
echo ""
echo "Installing the Application"
echo ""
cd "$DEMO_HOME"
if [ -f "setup/password_file.json" ]; then
  curl -H "Content-Type:multipart/form-data" -X POST -F "importData=@$DEMO_HOME/app/objects/$FUSION_APPLICATION_NAME.zip" -F 'variableValues=@"../setup/password_file.json"' "$FUSION_API/objects/import?importPolicy=overwrite"
else
  echo "No password variable file detected; attempting to create app without password bindings"
  echo ""
  curl -H "Content-Type:multipart/form-data" -X POST -F "importData=@$DEMO_HOME/app/objects/$FUSION_APPLICATION_NAME.zip"  "$FUSION_API/objects/import?importPolicy=overwrite"
fi
# Create the webapp
cd "$DEMO_HOME"
curl -H "content-type:application/json" -X POST -d "{\"id\": \"$FUSION_APPLICATION_NAME\",\"name\": \"$FUSION_APPLICATION_NAME\", \"contextPath\": \"/$FUSION_UI_NAME\"}" "$FUSION_API/webapps"
curl -H 'Content-type: application/zip' -X PUT "$FUSION_API/webapps/$FUSION_APPLICATION_NAME/war" --data-binary "@./app/dist/$FUSION_UI_ARTIFACT_ID.war"

echo ""
echo "Creating users"
echo ""
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Lawson", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Chloe", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Robert", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Cynthia", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Frank", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Geoffrey", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Carla", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"
curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H 'Content-type: application/json' -d '{"username":"Sophie", "password":"searchr0cks", "passwordConfirm":"searchr0cks", "realmName": "native", "roleNames": ["admin"]}' "$FUSION_USERS_API"

if [ "$no_crawl" -eq 0 ]; then
  sleep 10

  # Edit as you see fit to automate the running of datasources when someone does the install
  #echo ""
  #echo "Kicking off the Datasources"
  #echo ""
  #curl -u "$FUSION_USER:$FUSION_PASS" -X POST -H "Content-Type: application/json" -d '{"action": "start"}' "$FUSION_API_SECURE/jobs/datasource:compounds-crawler/actions"

fi
