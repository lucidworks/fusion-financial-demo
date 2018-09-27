package twigkit.security.header;

import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.preauth.PreAuthenticatedAuthenticationToken;

/**
 * An {@link AuthenticationProvider} that performs pre-authenticated authentication.
 *
 * @author scottbrown
 */
public class HeaderPreAuthenticationProvider implements AuthenticationProvider {

    /**
     * Perform authentication. In this case it is sufficient to just return the authentication request object.
     *
     * @param authentication the authentication request object
     * @return a fully authenticated object including credentials
     * @throws AuthenticationException if authentication fails
     */
    @Override
    public Authentication authenticate(Authentication authentication) throws AuthenticationException {
        return authentication;
    }

    /**
     * Check whether the given authentication object is supported by this authentication provider.
     *
     * @param authentication authentication object
     * @return <code>true</code> if this provider can evaluate the given authentication object
     */
    @Override
    public boolean supports(Class<?> authentication) {
        return authentication.equals(PreAuthenticatedAuthenticationToken.class);
    }
}