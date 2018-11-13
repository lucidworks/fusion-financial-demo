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
  cd "$DEMO_HOME/data/"
  mkdir "$DEMO_HOME/data/$FUSION_APPLICATION_NAME"
  touch "$DEMO_HOME/data/$FUSION_APPLICATION_NAME/.gitkeep"
fi
