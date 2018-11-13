package twigkit.client.processor.query;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.model.Filter;
import twigkit.model.Query;
import twigkit.processor.QueryProcessor;
import twigkit.social.ProfileContext;
import twigkit.social.model.Bookmark;
import twigkit.social.model.Profile;
import twigkit.social.service.persistence.AnnotationCriteria;
import twigkit.social.service.persistence.BookmarkDAO;

import java.util.List;

/**
 * Created by guywalker on 16/03/2017.
 * Modified by JohnGUnderwod on 20/04/2017.
 */
public class BookmarkQueryProcessor extends QueryProcessor {

    private static final Logger logger = LoggerFactory.getLogger(BookmarkQueryProcessor.class);

    public static String PARAMETER_TYPE = "type";


    @Inject
    private BookmarkDAO service;

    public Query change(Query query) {

        Profile profile = ProfileContext.getProfile();

        logger.trace("Fetching bookmark entries for user {} in database", profile.getUserId());
        if (profile != null) {
            AnnotationCriteria c = new AnnotationCriteria(null, profile);

            List<Bookmark> bookmarks = service.find(c);
            logger.trace("Found {} bookmark entries for user {}", bookmarks.size(), profile.getUserId());
            if (bookmarks.size() > 0) {
                // Add query filters
                for (Bookmark bookmark: bookmarks) {
                    String target = bookmark.getTarget();
                    if (target != null && target.length() > 0) {
                        logger.trace("Looking at bookmark target {}", target);

                        if (getParameterStringValue(PARAMETER_TYPE).equals("company")) {
                            Filter companyFilter = Filter.create("ticker_s", target, true, Filter.Optional.VALUE);
                            logger.trace("Adding filter {}", companyFilter.toString());
                            query.addFilter(companyFilter);

                        } else if (getParameterStringValue(PARAMETER_TYPE).equals("press-release")) {
                            Filter pressFilter = Filter.create("_lw_data_source_s", target + "-press-release", true, Filter.Optional.VALUE);
                            logger.trace("Adding filter {}", pressFilter.toString());
                            query.addFilter(pressFilter);
                        }
                    }

                    query.addOtherParameter("excludeFacet", false);
                }
            }
        }
        return query;
    }
}