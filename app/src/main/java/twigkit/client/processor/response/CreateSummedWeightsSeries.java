package twigkit.client.processor.response;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.model.Field;
import twigkit.model.Response;
import twigkit.model.Result;
import twigkit.processor.ResponseProcessor;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author JohnGUnderwood.
 * Adds a new result list as facts on response
 * Result list is set of unique values for specified field
 * Each result contains summed weight for values in specified field
 */
public class CreateSummedWeightsSeries extends ResponseProcessor {

    private static final Logger logger = LoggerFactory.getLogger(CreateSummedWeightsSeries.class);

    public static String PARAMETER_WEIGHT_FIELD = "weight-field";
    public static String PARAMETER_SUM_OVER_FIELD = "sum-over-field";

    @Override
    public Response change(Response response) {

        List<Result> results = response.getResults();
        Map<String,Float> summedWeights = new HashMap<String,Float>();

        for(Result r : results){
            String summedField = r.getFields().get(getParameterStringValue(PARAMETER_SUM_OVER_FIELD)).getValue().getActualAsString();
            Float weight = Float.parseFloat(r.getFields().get(getParameterStringValue(PARAMETER_WEIGHT_FIELD)).getValue().getActualAsString());

            if (summedWeights.containsKey(summedField)){
                summedWeights.replace(summedField,summedWeights.get(summedField)+weight);
            }
            else {
                summedWeights.put(summedField,weight);
            }
        }

        for( Map.Entry<String,Float> e : summedWeights.entrySet()){
            Result r = new Result();
            r.addField(new Field(getParameterStringValue(PARAMETER_SUM_OVER_FIELD),e.getKey()));
            r.addField(new Field(getParameterStringValue(PARAMETER_WEIGHT_FIELD),e.getValue()));
            r.setId(e.getKey());
            Map<String,Result> fact = new HashMap<>();
            fact.put("result",r);
            response.addFact(getParameterStringValue(PARAMETER_SUM_OVER_FIELD),fact);
        }

        return response;
    }
}
