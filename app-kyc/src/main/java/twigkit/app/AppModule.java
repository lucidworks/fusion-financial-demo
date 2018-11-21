package twigkit.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.AbstractTwigKitModule;

/**
 * Main application module
 *
 * @author scottbrown
 */
public class AppModule extends AbstractTwigKitModule {

    private static final Logger logger = LoggerFactory.getLogger(AppModule.class);

    public AppModule() {
        super(Priority.HIGHEST);
    }

    @Override
    protected void configure() {
        logger.info("Application Module loaded!");
    }
}
