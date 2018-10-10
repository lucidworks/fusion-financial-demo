package twigkit.app.inspection;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.AbstractTwigKitModule;
import twigkit.app.inspection.service.AppTitleService;
import twigkit.app.inspection.ws.AppTitleResource;


/**
 * Application module.
 *
 * @author bjarkih
 * @author brian
 */
public class AppInspectionModule extends AbstractTwigKitModule {

    private static final Logger logger = LoggerFactory.getLogger(AppInspectionModule.class);

    public AppInspectionModule() {
        super(Priority.LOWEST);
    }

    @Override
    protected void configure() {
        bind(AppTitleResource.class);
        bind(AppTitleService.class);

        logger.info("Application inspection module loaded");
    }
}
