#!/usr/bin/env bash

source ./bash-header.sh

source "$DEMO_HOME/myenv.sh"

echo ""
echo "Exporting $FUSION_APPLICATION_NAME App to $DEMO_HOME/app/$FUSION_APPLICATION_NAME.zip"
# !!!!!!!!!!!!!!!!!!!
# If you change this line, be sure to change clean.sh as well.
# TODO: change this to take in a location, optionally, so we can use this script from clean.sh
echo "Getting the Application Object"
echo ""
curl "$FUSION_API/objects/export?app.ids=$FUSION_APPLICATION_NAME" > "$DEMO_HOME/app/$FUSION_APPLICATION_NAME.zip"
#echo "Getting the UI Object"
#echo ""
# App Studio uses pre-auth cookies, so we need to get some cookies!  Mmm, me want cookies!
#curl -c target/cookies -i -H "content-type:application/json" -X POST -d "{\"username\":\"$FUSION_USER\", \"password\":\"$FUSION_PASS\"}" "$FUSION_API_SECURE_BASE/session"
#curl -b target/cookies  "$FUSION_APPKIT_PROJECT/$FUSION_UI_NAME" > "$DEMO_HOME/app/$FUSION_APPLICATION_NAME-ui.zip"

# If you have other applications you want as part of this, you can either add them into the respective calls above, or add them here
# See the ecommerce demo for examples

cd "$DEMO_HOME/app"
unzip -q -o -d ./objects "$FUSION_APPLICATION_NAME.zip"
rm "$FUSION_APPLICATION_NAME.zip"

#unzip -q -o "$FUSION_APPLICATION_NAME-ui.zip"
#rm "$FUSION_APPLICATION_NAME-ui.zip"

# Replace the artifact id so that install works
#SED_PATTERN="s|<artifactId>search-app</artifactId>|<artifactId>$FUSION_UI_NAME</artifactId>|g"
#sed -i.bak "$SED_PATTERN" pom.xml