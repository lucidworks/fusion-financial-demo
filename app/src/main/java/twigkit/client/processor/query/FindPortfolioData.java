package twigkit.client.processor.query;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.model.Filter;
import twigkit.model.Parameter;
import twigkit.model.Query;
import twigkit.processor.QueryProcessor;
import twigkit.social.ProfileContext;
import twigkit.social.model.Bookmark;
import twigkit.social.model.Profile;
import twigkit.social.model.Topic;
import twigkit.social.service.persistence.AnnotationCriteria;
import twigkit.social.service.persistence.BookmarkDAO;
import twigkit.social.service.persistence.TopicDAO;

import java.util.List;

/**
 * Created by guywalker on 16/03/2017.
 * Modified by JohnGUnderwod on 20/04/2017.
 */
public class FindPortfolioData extends QueryProcessor {

    private static final Logger logger = LoggerFactory.getLogger(FindPortfolioData.class);

    public static String PARAMETER_FILTER_FIELD = "filter_field";
    public static String PARAMETER_FILTER_SUFFIX = "suffix";
    public static String PARAMETER_FILTER_PREFIX = "prefix";


    @Inject
    private BookmarkDAO service;

    @Inject
    private TopicDAO topicService;

    public Query change(Query query) {

        Profile profile = ProfileContext.getProfile();

        String field;
        if(hasParameter(PARAMETER_FILTER_FIELD)){
            field = getParameterStringValue(PARAMETER_FILTER_FIELD);
        }else{
            field = "_lw_data_source_s";
        }

        String prefix = "";
        if(hasParameter(PARAMETER_FILTER_PREFIX)){
            prefix = getParameterStringValue(PARAMETER_FILTER_PREFIX);
        }

        String suffix = "";
        if(hasParameter(PARAMETER_FILTER_SUFFIX)){
            suffix = getParameterStringValue(PARAMETER_FILTER_SUFFIX);
        }

        logger.debug("Fetching bookmark entries for user {} in database", profile.getUserId());
        if (profile != null) {

            // Get custom 'portfolio' param off query to restrict to specific portfolio topic.
            Parameter portfolio = query.getCustomParameters().getParameter("portfolio");

            AnnotationCriteria c;

            if(portfolio != null ){
                String topicId = portfolio.getValue().toString();
                logger.debug("Filtering by topic ID {}",topicId);
                Topic topic = topicService.get(Long.parseLong(topicId));
                c = new AnnotationCriteria(null, profile, topic);
            }else{
                c = new AnnotationCriteria(null, profile);
            }

            List<Bookmark> bookmarks = service.find(c);
            logger.trace("Found {} bookmark entries for user {}", bookmarks.size(), profile.getUserId());
            if (bookmarks.size() > 0) {
                // Add query filters
                for (Bookmark bookmark: bookmarks) {
                    String target = bookmark.getTarget();
                    if (target != null && target.length() > 0) {
                        logger.trace("Looking at bookmark target {}", target);

                        Filter pressFilter = Filter.create(field, prefix + target + suffix, true, Filter.Optional.VALUE);
                        logger.debug("Adding filter {}", pressFilter.toString());
                        query.addFilter(pressFilter);

                    }

                    query.addOtherParameter("excludeFacet", false);
                }
            }
        }
        return query;
    }
}