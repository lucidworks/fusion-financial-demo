package twigkit.security.provider;

import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.GrantedAuthority;

import java.util.Collection;
import java.util.Collections;

/**
 * All requests are mapped to a single fixed system user.
 *
 * @author Bjarki Holm
 */
public class FixedAuthenticationProvider implements AuthenticationProvider {

    @Override
    public Authentication authenticate(Authentication authentication) throws AuthenticationException {
        return new FixedAuthentication();
    }

    @Override
    public boolean supports(Class<?> aClass) {
        return true;
    }

    static class FixedAuthentication implements Authentication {

        public static final String PRINCIPAL = "fixed-user";

        @Override
        public Collection<? extends GrantedAuthority> getAuthorities() {
            return Collections.emptySet();
        }

        @Override
        public Object getCredentials() {
            return PRINCIPAL;
        }

        @Override
        public Object getDetails() {
            return Collections.emptyMap();
        }

        @Override
        public Object getPrincipal() {
            return PRINCIPAL;
        }

        @Override
        public boolean isAuthenticated() {
            return true;
        }

        @Override
        public void setAuthenticated(boolean isAuthenticated) throws IllegalArgumentException {
        }

        @Override
        public String getName() {
            return PRINCIPAL;
        }
    }
}
