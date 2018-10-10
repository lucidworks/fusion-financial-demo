package twigkit.app.inspection.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.fig.Config;
import twigkit.fig.Fig;
import twigkit.util.FigUtils;

/**
 * Get the application-title from fig.
 *
 * @author KieranDotCo
 */
public class AppTitleService {

    private static final Logger logger = LoggerFactory.getLogger(AppTitleService.class);

    private static final Fig fig = Fig.getInstance(FigUtils.getApplicationLoader());

    private static final Config config = fig.get("platforms", "fusion", "data");

    public final String TITLE = "application-title";

    /**
     * @return the UI's application-title.
     * @author KieranDotCo
     */
    public String getTitle() {
      return config.value(TITLE).as_string();
    }
}
