#!/usr/bin/env bash

source ./bash-header.sh
set -x

source "$DEMO_HOME/myenv.sh"

echo "Exporting the App just in case to /tmp/$FUSION_APPLICATION_NAME.zip"
curl "$FUSION_API/objects/export?app.ids=$FUSION_APPLICATION_NAME" > "$DEMO_HOME/app/$FUSION_APPLICATION_NAME.zip"

curl  -X DELETE "$FUSION_API/webapps/$FUSION_UI_NAME"
curl  -X DELETE "$FUSION_API/webapps/data"
curl  -X DELETE "$FUSION_API/apps/$FUSION_APPLICATION_NAME"

# Do any other deletes that you want