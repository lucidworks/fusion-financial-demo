package twigkit.security.provider;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import twigkit.fig.Config;
import twigkit.fig.Fig;
import twigkit.util.FigUtils;

/**
 * Authentication provider that delegates the decision on authentication to one of a set of
 * pre-defined authentication providers. The particular delegate provider used is determined
 * by the value of {@code security.type} in the application's configuration.
 *
 * @author Bjarki Holm
 */
public class DelegateAuthenticationProvider implements AuthenticationProvider {

    private static final Logger logger = LoggerFactory.getLogger(DelegateAuthenticationProvider.class);

    /** The delegate instance */
    private AuthenticationProvider delegate;

    protected synchronized void configure() {
        logger.debug("Configuring a delegate authentication provider");
        delegate = new FixedAuthenticationProvider();
        Fig fig = Fig.getInstance(FigUtils.getApplicationLoader());
        if (fig != null) {
            Config config = fig.get("security", "delegate");
            if (config != null && config.has("name")) {
                String fqcn = config.value("name").as_string();
                try {
                    delegate = (AuthenticationProvider) Class.forName(fqcn).newInstance();
                    logger.debug("Instantiated a new authentication provider of type {}", fqcn);
                } catch (Exception e) {
                    logger.error("Error when instantiating authentication provider", e);
                }
            }
        }
    }

    @Override
    public Authentication authenticate(Authentication authentication) throws AuthenticationException {
        if (delegate == null) {
            configure();
        }
        return delegate.authenticate(authentication);
    }

    @Override
    public boolean supports(Class<?> aClass) {
        return true;
    }
}
