package twigkit.client.processor.response;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.conf.ConfiguredPlatformProvider;
import twigkit.model.*;
import twigkit.platform.Platform;
import twigkit.processor.ResponseProcessor;

import java.util.List;

/**
 * Execute a secondary pivot facet query to fetch related news metadata
 * for every company result in a result set.
 *
 * @author bjarkih
 */
public class FetchRelatedNews extends ResponseProcessor {

    private static final Logger logger = LoggerFactory.getLogger(FetchRelatedNews.class);

    public static String PARAMETER_FILTER_SUFFIX = "filter-value-suffix";
    public static String PARAMETER_FILTER_FIELD = "filter-field";
    public static String PARAMETER_ID_FIELD = "id-field";
    public static String PARAMETER_METADATA_FIELD = "metadata-field";

    public static String PARAMETER_PIVOT = "pivot";

    public static String PARAMETER_PLATFORM = "news-platform";

    private static Boolean USE_PARTIAL = false;

    @Inject
    private ConfiguredPlatformProvider platformProvider;

    @Override
    public void setup(){
        if(!hasParameter(PARAMETER_FILTER_SUFFIX)){
            setParameterValue(PARAMETER_FILTER_SUFFIX,"");
        }

//        Check if string that is passed in contains a wildcard
        String filterSuffix = getParameterStringValue(PARAMETER_FILTER_SUFFIX);
        if(filterSuffix.endsWith("*")){
            USE_PARTIAL = true;
            setParameterValue(PARAMETER_FILTER_SUFFIX,filterSuffix.substring(0, filterSuffix.length() - 1));
        }
    }

    @Override
    public Response change(Response companies) {

        String newsPlatformId = getParameterStringValue(PARAMETER_PLATFORM);
        Platform newsPlatform = platformProvider.get(newsPlatformId);


        Query newsQuery = new Query();
        newsQuery.setResultsPerPage(0);
        newsQuery.setFacets("");
        newsQuery.addCustomParameter("facet.pivot", getParameterStringValue(PARAMETER_PIVOT));
        newsQuery.addCustomParameter("facet.pivot.mincount", "1");

        // Filter on the current companies
        String dataSourceField = getParameterStringValue(PARAMETER_FILTER_FIELD);
        String fieldValueSuffix = getParameterStringValue(PARAMETER_FILTER_SUFFIX);

        String idField = getParameterStringValue(PARAMETER_ID_FIELD);
        companies.getResults().forEach(r -> {
            Filter filter = new Filter(dataSourceField, r.getFields().get(idField).getValue().getActualAsString() + fieldValueSuffix);
            if(USE_PARTIAL){
                filter.setMatch(Filter.Match.RIGHT_PARTIAL);
            }
            filter.setOptional(Filter.Optional.VALUE);
            newsQuery.addFilter(filter);
        });

        Response relatedNews = newsPlatform.search(newsQuery);
        String facetName = getParameterStringValue(PARAMETER_PIVOT).replaceAll(",", "-");
        Facet facet = relatedNews.getFacet(facetName);

        logger.debug("Got back {} entries for facet {}", facet != null ? facet.getFilters().size() : 0, facetName);

        //_lw_data_source_s-Company_Events_ss'].filters" ng-if="filter.val==result.fields.ticker_s.val[0]+'-press-release'">

        // Glue related news metadata onto each company record
        String metadataFieldName = getParameterStringValue(PARAMETER_METADATA_FIELD);
        companies.getResults().forEach(r -> {
            facet.getFilters().forEach(f -> {
                String filterValue = f.getValue().getActualAsString();
                String companyId = r.getFields().get(idField).getValue().getActualAsString();
//                Strip off stock exchange ID
                String ticker = filterValue.split("\\.")[0];
//                if (filterValue.equalsIgnoreCase(companyId + fieldValueSuffix))
                if (ticker.equalsIgnoreCase(companyId)){
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
