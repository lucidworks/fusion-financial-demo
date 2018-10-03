package twigkit.client.processor.response;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.conf.ConfiguredPlatformProvider;
import twigkit.model.*;
import twigkit.platform.Platform;
import twigkit.processor.ResponseProcessor;
import twigkit.search.processors.response.DateFacetValueFormatter;

import java.util.List;

/**
 * Execute a secondary pivot facet query to fetch related news metadata
 * for every company result in a result set.
 *
 * @author bjarkih
 */
public class FetchRelatedNews extends ResponseProcessor {

    private static final Logger logger = LoggerFactory.getLogger(FetchRelatedNews.class);

    @Inject
    private ConfiguredPlatformProvider platformProvider;

    @Override
    public Response change(Response companies) {

        String newsPlatformId = getParameterStringValue("news-platform");
        Platform newsPlatform = platformProvider.get(newsPlatformId);


        Query newsQuery = new Query();
        newsQuery.setResultsPerPage(0);
        newsQuery.setFacets("");
        newsQuery.addCustomParameter("facet.pivot", getParameterStringValue("pivot"));
        newsQuery.addCustomParameter("facet.pivot.mincount", "1");

        // Filter on the current companies
        String dataSourceField = getParameterStringValue("datasource-field");
        String fieldValueSuffix = getParameterStringValue("field-suffix");
        String idField = getParameterStringValue("id-field");
        companies.getResults().forEach(r -> {
            Filter filter = new Filter(dataSourceField, r.getFields().get(idField).getValue().getActualAsString() + fieldValueSuffix);
            filter.setOptional(Filter.Optional.VALUE);
            newsQuery.addFilter(filter);
        });

        Response relatedNews = newsPlatform.search(newsQuery);
        String facetName = getParameterStringValue("pivot").replaceAll(",", "-");
        Facet facet = relatedNews.getFacet(facetName);

        logger.debug("Got back {} entries for facet {}", facet != null ? facet.getFilters().size() : 0, facetName);

        //_lw_data_source_s-Company_Events_ss'].filters" ng-if="filter.val==result.fields.ticker_s.val[0]+'-press-release'">

        // Glue related news metadata onto each company record
        String metadataFieldName = getParameterStringValue("metadata-field");
        companies.getResults().forEach(r -> {
            facet.getFilters().forEach(f -> {
                String filterValue = f.getValue().getActualAsString();
                String companyId = r.getFields().get(idField).getValue().getActualAsString();
                if (filterValue.equalsIgnoreCase(companyId + fieldValueSuffix)) {
                    Field metadata = new Field(metadataFieldName);
                    logger.debug("Found {} related news for company {}", f.getRelatedFilters().size(), companyId);
                    List<FacetFilter> filters = f.getRelatedFilters();
                    filters.forEach(val -> {
                        metadata.addValue(new Value(val.getValue().getActualAsString()));
                    });
                    r.addField(metadata);
                }
            });
        });

        return companies;
    }
}
