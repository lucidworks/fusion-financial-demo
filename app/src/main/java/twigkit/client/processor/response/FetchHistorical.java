package twigkit.client.processor.response;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.conf.ConfiguredPlatformProvider;
import twigkit.model.Filter;
import twigkit.model.Query;
import twigkit.model.Response;
import twigkit.platform.Platform;
import twigkit.processor.ResponseProcessor;

/**
 * Execute a secondary pivot facet query to fetch stock history for every company result in a result set.
 *
 * @author bjarkih
 */
public class FetchHistorical extends ResponseProcessor {

    private static final Logger logger = LoggerFactory.getLogger(FetchHistorical.class);

    @Inject
    private ConfiguredPlatformProvider platformProvider;

    @Override
    public Response change(Response companies) {

        String historicalPlatformId = getParameterStringValue("historical-platform");
        Platform historicalPlatform = platformProvider.get(historicalPlatformId);


        // Filter on the current companies
        String dataSourceField = getParameterStringValue("datasource-field");
        String dataSourceValue = getParameterStringValue("datasource-value");
        String idField = getParameterStringValue("id-field");

        logger.debug("Iterating over {} results.",companies.getHits());

        companies.getResults().forEach(r -> {
            logger.trace("Processing result {}.",r.getId());

            Query historicalQuery = new Query();
            historicalQuery.setUser(companies.getQuery().getUser());
            historicalQuery.setFields("high_d,low_d,close_d,ticker_s");
            historicalQuery.setResultsPerPage(getParameterIntegerValue("results-to-fetch"));
            historicalQuery.setSorts("-date_dt");

            if(r.getFields().get(idField) == null){
                logger.error("Result did not contain field {}",idField);
            }else{
                String company = r.getFields().get(idField).getValue().getActualAsString();
                Filter filter = new Filter(dataSourceField, dataSourceValue);
                filter.setOptional(Filter.Optional.VALUE);
                historicalQuery.addFilter(filter);

                filter = new Filter(idField, company);
                filter.setOptional(Filter.Optional.VALUE);
                historicalQuery.addFilter(filter);

                Response relatedResults = historicalPlatform.search(historicalQuery);

                logger.debug("Got back {} related results for {} ", relatedResults != null ? relatedResults.getResults().size() : 0, company);

                relatedResults.getResults().forEach(related -> {
                    r.addRelated(related);
                });
            }

        });

        return companies;
    }
}
