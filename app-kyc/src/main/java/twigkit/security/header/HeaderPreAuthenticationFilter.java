package twigkit.security.header;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.preauth.AbstractPreAuthenticatedProcessingFilter;
import twigkit.TwigKitApplication;
import twigkit.fusion.api.session.FusionSession;
import twigkit.fusion.api.session.FusionSessionStore;
import twigkit.fusion.api.session.FusionSessionUtils;
import twigkit.security.fusion.FusionAuthentication;

import javax.servlet.http.HttpServletRequest;

/**
 * A Spring Security filter that handles pre-authenticated authentication requests. This will return a non-null
 * username when the user has already been authenticated against Fusion.
 *
 * @author scottbrown
 */
public class HeaderPreAuthenticationFilter extends AbstractPreAuthenticatedProcessingFilter {

    private static final Logger logger = LoggerFactory.getLogger(HeaderPreAuthenticationFilter.class);

    private static final String USER_NAME = "fusion-user-name";

    public HeaderPreAuthenticationFilter() {
        setCheckForPrincipalChanges(true);
    }

    /**
     * Check if the user has already been authenticated and if so return the username.
     *
     * @param request incoming request
     * @return the name of the pre-authenticated user or null
     */
    @Override
    protected Object getPreAuthenticatedPrincipal(HttpServletRequest request) {
        String username = request.getHeader(USER_NAME);

        if (username != null) {
            logger.debug("{} already authenticated against Fusion", username);
            FusionSessionStore sessionStore = TwigKitApplication.getInstance().getInjector().getInstance(FusionSessionStore.class);
            FusionSession fusionSession = FusionSessionUtils.fromCookies(username, request.getCookies());

            if (fusionSession != null) {
                logger.debug("Updating session store for {}", username);
                sessionStore.set(username, fusionSession);
                return username;
            } else {
                logger.debug("No Fusion session cookie found in request - unable to sync session store. " +
                        "Redirecting {} to re-authenticate", username);
                return null;
            }
        }

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        return authentication != null && authentication instanceof FusionAuthentication ?
                authentication.getName() : null;
    }

    /**
     * Extract the credentials (if applicable) from the current request.
     *
     * @param request incoming request
     * @return the name of the current user
     */
    @Override
    protected Object getPreAuthenticatedCredentials(HttpServletRequest request) {
        return getPreAuthenticatedPrincipal(request);
    }
}
