


object SolrToParquet {


  def main(args: Array[String]) {
    val dir = args(0)
    //TODO: fix this so we just pass in the list of collections to dump
    val collections = List("COLL A", "COLL B")
    //"ecommerce_signals_recs", "ecommerce_signals_item_sims",
    //val collections = List("ecommerce_training")

    collections.foreach(coll => {
      val theMap = Map("collection" -> coll, "query" -> "*:*", "flatten_multivalued" -> "false", "exclude_fields" -> "score,_version_")
      println("Dumping: " + coll + " to " + dir)
      val theDF = spark.read.format("solr").options(theMap).load
      theDF.repartition(1).write.parquet(dir + "/" + coll)
    })
  }
}

val str = sc.getConf.get("spark.driver.args")
//System.out.println(str)
val args = str.split("\\|")
//System.out.println(args)
SolrToParquet.main(args)
System.exit(0)