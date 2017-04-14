#!/usr/bin/env bash


echo "Importing Fusion config"
curl -u admin:password123 -H "Content-Type:multipart/form-data" -X POST -F 'importData=@fusion-config.json' http://localhost:8764/api/apollo/objects/import?importPolicy=overwrite
echo "Adding Schema"
curl -u admin:password123 -X POST -H 'Content-type:application/json' --data-binary @schema.json "http://localhost:8764/api/apollo/solr/finance/schema"