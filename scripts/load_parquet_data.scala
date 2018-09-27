import java.util.{Calendar, Locale, TimeZone}


object LoadProductsIntoSolr extends Serializable {

  def main(args: Array[String]) {
    val dir = args(0)
    //TODO: fix this so we just pass in the list of collections to dump
    //Fill in the collections you want to load
    val collections = List("COLL A", "COLL_B")
    //Loop over all the collections and load them in.  Do some special handling for ecommerce_signals
    collections.foreach(coll => {
      println("Loading: " + coll + " from " + dir)
      //probably a better scala way to do this
      spark.read.parquet(dir + "/" + coll + "/*.parquet").write.format("solr").options(Map("collection" -> coll, "commit_within" -> "5000")).save
    })
  }
}

val str = sc.getConf.get("spark.driver.args")
//System.out.println(str)
val args = str.split("\\|")
//System.out.println(args)
LoadProductsIntoSolr.main(args)
System.exit(0)
