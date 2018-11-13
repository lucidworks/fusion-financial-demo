import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.SolrInputField;
import org.apache.solr.common.params.MapSolrParams;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Tool to seek and destroy and bad TRIT tags.
 */
public class TritSweeper {

    private static Set<String> BAD_PERSONS = Sets.newHashSet(
            "Blacklist Ad-Free",
            "Fortune Dow",
            "Investing",
            "Trump",
            "Investing",
            "Says Bloomberg Westford"

    );
    public static void main(String[] args) throws Exception {
        final SolrClient client = getSolrClient("http://localhost:8983/solr");
        final SolrClient updateClient = getSolrClient("http://localhost:8983/solr/Finance");

        final Map<String, String> queryParamMap = new HashMap<String, String>();
        queryParamMap.put("q", "*:*");
        queryParamMap.put("fq", "_lw_data_source_s:yahoo-news");
        queryParamMap.put("fl", "*");
        queryParamMap.put("rows", "100000");
        MapSolrParams queryParams = new MapSolrParams(queryParamMap);

        final QueryResponse response = client.query("Finance", queryParams);
        final SolrDocumentList documents = response.getResults();

        for(SolrDocument document : documents) {
            if (document == null) {
                continue;
            }
            List<String> newPersons = Lists.newArrayList();
            SolrInputDocument inputDoc = new SolrInputDocument();
            for (String fieldName : document.getFieldNames()) {
                if (fieldName.equals("_version_")) {
                    continue;
                }
                SolrInputField inputField = new SolrInputField(fieldName);
                for (Object v : document.getFieldValues(fieldName)) {
                    inputField.addValue(v);
                }
                inputDoc.put(fieldName, inputField);
            }
            boolean needUpdate = false;
            if (document.getFieldValues("entity_person_hv_ss") != null) {
                for (Object person : document.getFieldValues("entity_person_hv_ss")) {
                    String personStr = person.toString();
                    if (BAD_PERSONS.contains(personStr)) {
                        needUpdate = true;
                    } else {
                        newPersons.add(personStr);
                    }
                }
                if (needUpdate) {
                    inputDoc.removeField("entity_person_hv_ss");
                    SolrInputField inputField = new SolrInputField("entity_person_hv_ss");
                    for (String v : newPersons) {
                        inputField.addValue(v);
                    }
                    inputDoc.put("entity_person_hv_ss", inputField);
                    updateClient.add(inputDoc);
                    System.out.println("Updated a document!");
                }
            }
        }

        updateClient.commit();
    }

    private static SolrClient getSolrClient(String solrUrl) {
        return new HttpSolrClient.Builder(solrUrl)
                .withConnectionTimeout(10000)
                .withSocketTimeout(60000)
                .build();
    }
}
