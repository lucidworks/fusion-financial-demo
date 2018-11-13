package twigkit.client.processor.response;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.conf.ConfiguredPlatformProvider;
import twigkit.model.Filter;
import twigkit.model.Query;
import twigkit.model.Response;
import twigkit.model.values.Range;
import twigkit.platform.Platform;
import twigkit.processor.ResponseProcessor;

/**
 * Execute a secondary pivot facet query to fetch account info per client.
 */
public class FetchAccounts extends ResponseProcessor {

    private static final Logger logger = LoggerFactory.getLogger(FetchAccounts.class);

    @Inject
    private ConfiguredPlatformProvider platformProvider;

    @Override
    public Response change(Response accounts) {

        String accountsPlatformId = getParameterStringValue("accounts-platform");
        Platform accountsPlatform = platformProvider.get(accountsPlatformId);


        // Filter on the current companies
        String dataSourceField = getParameterStringValue("datasource-field");
        String dataSourceValue = getParameterStringValue("datasource-value");
        String idField = getParameterStringValue("id-field");

        logger.debug("Iterating over {} results.",accounts.getHits());

        accounts.getResults().forEach(r -> {
            logger.trace("Processing result {}.",r.getId());

            Query accountsQuery = new Query();
            accountsQuery.setUser(accounts.getQuery().getUser());
            accountsQuery.setFields("type_s");
            accountsQuery.setResultsPerPage(getParameterIntegerValue("results-to-fetch"));
            accountsQuery.setSorts("-open_dt");

            if(r.getFields().get(idField) == null){
                logger.error("Result did not contain field {}",idField);
            }else{
                String company = r.getFields().get(idField).getValue().getActualAsString();
                Filter filter = new Filter(dataSourceField, dataSourceValue);
                filter.setOptional(Filter.Optional.VALUE);
                accountsQuery.addFilter(filter);

                filter = new Filter(idField, company);
                filter.setOptional(Filter.Optional.VALUE);
                accountsQuery.addFilter(filter);

                Response relatedResults = accountsPlatform.search(accountsQuery);

                logger.debug("Got back {} related results for {} ", relatedResults != null ? relatedResults.getResults().size() : 0, company);

                relatedResults.getResults().forEach(related -> {
                    r.addRelated(related);
                });
            }

        });

        return accounts;
    }
}
