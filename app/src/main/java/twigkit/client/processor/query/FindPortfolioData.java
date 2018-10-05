package twigkit.client.processor.query;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.model.Filter;
import twigkit.model.Query;
import twigkit.processor.QueryProcessor;

/**
 * Created by JohnGUnderwod on 05/10/2018.
 * Users' portfolio/buckets of companies are indexed into Fusion to get press releases
 *
 */
public class FindPortfolioData extends QueryProcessor {

    private static final Logger logger = LoggerFactory.getLogger(FindPortfolioData.class);

    public static String PARAMETER_FILTER_FIELD = "filter_field";
    public static String PARAMETER_DATA_SOURCE = "data_source";
    public static String PARAMETER_USER_PARAM = "user_filter";

    public Query change(Query query) {

        String username = query.getCustomParameters().getParameterStringValue(PARAMETER_USER_PARAM);

        query.addFilter(new Filter(getParameterStringValue(PARAMETER_FILTER_FIELD),username));
        query.addFilter(new Filter("_lw_data_source_s",getParameterStringValue(PARAMETER_DATA_SOURCE)));

        return query;
    }
}