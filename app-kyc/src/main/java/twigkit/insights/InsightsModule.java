package twigkit.insights;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.AbstractTwigKitModule;
import twigkit.insights.rest.InsightsResource;

public class InsightsModule extends AbstractTwigKitModule {

	private static final Logger logger = LoggerFactory.getLogger(InsightsModule.class);

    @Override
    protected void configure() {
        bind(InsightsResource.class);
        logger.info("Insights Module loaded!");
    }

}
