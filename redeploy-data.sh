#!/usr/bin/env bash

source ./bash-header.sh
source "$DEMO_HOME/myenv.sh"

OPTIND=1
offline=


while getopts "o" opt; do
    case "$opt" in
    o)  offline="-o"
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

echo "Offline=$offline, Leftovers: $@"


curl  -X DELETE "$FUSION_API/webapps/data"


cd "$DEMO_HOME/data"
jar -cf ../target/data.war index.html "$FUSION_APPLICATION_NAME"/*.*

cd "$DEMO_HOME/setup"

echo "Redeploying the Data"
echo ""
curl -H 'Content-type: application/json' -X POST -d "@data_appstudio.json" "$FUSION_API/webapps"
curl -H 'Content-type: application/zip' -X PUT "$FUSION_API/webapps/data/war" --data-binary "@../target/data.war"

