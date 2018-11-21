package twigkit.app.auth;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.DefaultRedirectStrategy;
import org.springframework.security.web.RedirectStrategy;
import org.springframework.security.web.authentication.LoginUrlAuthenticationEntryPoint;
import twigkit.util.ESAPIEncoder;
import twigkit.util.Encoder;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Redirect users to fusion admin login when trying to access a setup url (eg. /apps/<app-name>/setup)
 *
 * @author bjarkih
 * @author KieranDotCo
 */
public class SetupAuthenticationRedirectEntryPoint extends LoginUrlAuthenticationEntryPoint {

    private static final Logger logger = LoggerFactory.getLogger(SetupAuthenticationRedirectEntryPoint.class);

    private Encoder encoder;

    public static final String REDIRECT_PARAM = "return";
    public static final String PORT = "8764";

    public SetupAuthenticationRedirectEntryPoint(String loginFormUrl) {
        super(loginFormUrl);
        this.encoder = new ESAPIEncoder();
    }

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
            AuthenticationException authenticationException) throws IOException, ServletException {
        RedirectStrategy redirectStrategy = new DefaultRedirectStrategy();
                
        final String requestUri = request.getRequestURI();

        final String redirectUrl = new StringBuffer(request.getScheme()).append("://")
            .append(request.getServerName()).append(":")
            .append(PORT)
            .append(getLoginFormUrl())
            .append('?').append(REDIRECT_PARAM).append('=').append(encoder.encodeForURL(requestUri))
            .toString();

        logger.debug("Redirecting user to signin URL {}", redirectUrl);

        redirectStrategy.sendRedirect(request, response, redirectUrl);
    }
}
