source ./bash-header.sh
source ./myenv.sh

"$FUSION_HOME/bin/spark-shell" -m 4g -c 4 -i "$DEMO_HOME/scripts/dump_solr_to_parquet.scala" --conf spark.driver.args="'$DEMO_HOME/data/parquet'"