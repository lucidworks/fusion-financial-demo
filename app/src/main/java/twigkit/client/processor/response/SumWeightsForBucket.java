package twigkit.client.processor.response;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.model.Field;
import twigkit.model.Response;
import twigkit.model.Result;
import twigkit.processor.ResponseProcessor;

import java.util.*;
import java.util.stream.Collectors;

/**
 * @author JohnGUnderwood.
 * Sum weights per industry for companies grouped into buckets on response
 */
public class SumWeightsForBucket extends ResponseProcessor {

    private static final Logger logger = LoggerFactory.getLogger(SumWeightsForBucket.class);

    public static String PARAMETER_WEIGHT_FIELD = "weight-field";
    public static String PARAMETER_SUM_OVER_FIELD = "sum-over-field";
    public static String PARAMETER_SUMMED_FIELD = "summed-field";


    @Override
    public Response change(Response grouped) {

        List<Result> buckets = grouped.getResults();
        List<Result> newBuckets = new ArrayList<>();

        for(Result r : buckets){
            Map<String,Float> summedWeights = new HashMap<String,Float>();

            List<Result> companies = r.getRelated();
            for(Result c : companies){
                String summedField = c.getFields().get(getParameterStringValue(PARAMETER_SUM_OVER_FIELD)).getValue().getActualAsString();
                Float weight = Float.parseFloat(c.getFields().get(getParameterStringValue(PARAMETER_WEIGHT_FIELD)).getValue().getActualAsString());

                if (summedWeights.containsKey(summedField)){
                    summedWeights.replace(summedField,summedWeights.get(summedField)+weight);
                }
                else {
                    summedWeights.put(summedField,weight);
                }
            }

            Map<String,Float> sortedWeights = summedWeights
                    .entrySet()
                    .stream()
                    .sorted(Collections.reverseOrder(Map.Entry.comparingByValue()))
                    .collect(
                            Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (e1, e2) -> e2,
                                    LinkedHashMap::new));

            for( Map.Entry<String,Float> e : sortedWeights.entrySet()){
                r.addField(new Field(e.getKey(),e.getValue()));
                r.addField(new Field(getParameterStringValue(PARAMETER_SUMMED_FIELD),e.getKey()));
            }

            newBuckets.add(r);
        }

        grouped.setResults(newBuckets);
        return grouped;
    }
}
