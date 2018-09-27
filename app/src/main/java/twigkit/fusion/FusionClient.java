package twigkit.fusion;

import org.apache.commons.io.IOUtils;
import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.client.CookieStore;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.cookie.Cookie;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.BasicCookieStore;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.apache.http.impl.cookie.DefaultCookieSpec;
import org.codehaus.jettison.json.JSONArray;
import org.codehaus.jettison.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.PlatformClient;
import twigkit.TwigKitApplication;
import twigkit.fusion.api.session.FusionSession;
import twigkit.fusion.api.session.FusionSessionStore;
import twigkit.http.util.HttpClientFactory;
import twigkit.model.auth.User;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Fusion API client.
 *
 * @author stefan@lucidworks.com
 */
public class FusionClient extends PlatformClient {

    private static final Logger logger = LoggerFactory.getLogger(FusionClient.class);

    public static final String DEFAULT_HOST = "localhost";
    public static final int DEFAULT_PORT = 8764;

    private static final String HTTP = "http";
    private static final String ID = "id";
    private static final String USERNAME = "username";
    private static final String PASSWORD = "password";
    private static final String API_ENDPOINT = "/api";
    private static final String SESSION_ENDPOINT = "/api/session";
    private static final String REALM_PARAMETER = "realmName";
    private static final String ENABLED_REALMS = "enabledRealms";
    private static final String[] REALMS_TO_REMOVE = {"webapps-jwt-realm"};

    private CloseableHttpClient httpClient;
    private String sessionId;
    private String host;
    private int port;

    public FusionClient(CloseableHttpClient httpClient) {
        this.httpClient = httpClient;
        port = -1;
    }

    public CloseableHttpClient getHttpClient() {
        return httpClient;
    }

    public String getSessionId() {
        return sessionId;
    }

    public String getHost() {
        return host;
    }

    public void setHost(String host) {
        this.host = host;
    }

    public int getPort() {
        return port;
    }

    public void setPort(int port) {
        this.port = port;
    }

    /**
     * Checking if instance is running locally on standard port.
     *
     * @return
     */
    public static boolean hasLocal() {
        return ping(DEFAULT_HOST, DEFAULT_PORT);
    }

    /**
     * Get a list of authentication realms for a given Fusion instance before
     * attempting authentication.
     *
     * @param host
     * @return
     * @throws Exception
     */
    public static List<String> realms(String host, int port) throws Exception {
        List<String> realms = new ArrayList<>();

        try (CloseableHttpClient httpClient = HttpClientFactory.get()) {
            URIBuilder uri = new URIBuilder();
            uri.setScheme(HTTP).setHost(host).setPort(port).setPath(API_ENDPOINT);

            final HttpGet realmRequest = new HttpGet(uri.build());
            HttpResponse realmResponse = httpClient.execute(realmRequest);
            JSONObject json = new JSONObject(IOUtils.toString(realmResponse.getEntity().getContent()));

            JSONArray enabledRealms = json.getJSONArray(ENABLED_REALMS);
            for (int i = 0; i < enabledRealms.length(); i++) {
                final String realm = enabledRealms.getJSONObject(i).getString("name");

                if (!Arrays.asList(REALMS_TO_REMOVE).contains(realm)) {
                    realms.add(realm);
                }
            }
        }

        return realms;
    }

    /**
     * Get a session from Fusion for subsequent API calls.
     *
     * @param host
     * @param realm
     * @param user
     * @param password
     * @return
     * @throws Exception
     */
    public static FusionClient session(String host, int port, String realm, String user, String password) throws Exception {
        FusionClient fusionClient = new FusionClient(HttpClientFactory.get());
        fusionClient.host = host;
        fusionClient.port = port;

        HttpClientContext context = HttpClientContext.create();

        URIBuilder uri = new URIBuilder();
        uri.setScheme(HTTP).setHost(host).setPort(port).setPath(SESSION_ENDPOINT).setParameter(REALM_PARAMETER, realm);

        final HttpPost sessionRequest = new HttpPost(uri.build());

        JSONObject payload = new JSONObject();
        payload.put(USERNAME, user);
        payload.put(PASSWORD, password);

        sessionRequest.setEntity(new StringEntity(payload.toString(), ContentType.APPLICATION_JSON));

        String response = IOUtils.toString(fusionClient.getHttpClient().execute(sessionRequest, context).getEntity().getContent());

        CookieStore cookieStore = context.getCookieStore();
        for (Cookie cookie : cookieStore.getCookies()) {
            if (cookie.getName().equals(ID)) {
                fusionClient.sessionId = cookie.getValue();
                return fusionClient;
            }
        }

        throw new IOException(response);
    }

    /**
     * Make a request to a Fusion Endpoint.
     *
     * @param endpoint
     * @return
     * @throws Exception
     */
    public String request(String endpoint) throws Exception {
        return request(endpoint, null);
    }

    /**
     * Make a request to a Fusion Endpoint.
     *
     * @param endpoint the requested endpoint
     * @param user     the current user
     * @return the JSON response from Fusion
     * @throws Exception if it's not possible to make a reqest to Fusion
     */
    public String request(String endpoint, User user) throws Exception {
        String host = this.host != null ? this.host : DEFAULT_HOST;
        int port = this.port != -1 ? this.port : DEFAULT_PORT;

        URIBuilder uri = new URIBuilder();
        uri.setScheme(HTTP).setHost(host).setPort(port).setPath(endpoint);
        logger.debug("Requested URI: {}", uri.getScheme() + "://" + uri.getHost() + ":" + uri.getPort() + uri.getPath());

        final HttpGet request = new HttpGet(uri.build());

        HttpResponse httpResponse;
        if (user != null && (sessionId == null || sessionId.isEmpty())) {
            FusionSessionStore sessionStore = TwigKitApplication.getInstance().getInjector().getInstance(FusionSessionStore.class);
            FusionSession fusionSession = sessionStore.get(user.getId());

            if (fusionSession == null) {
                throw new NullPointerException("No session found for user " + user.getId());
            }

            logger.debug("Making a request to Fusion for user {} ", user.getId());
            httpResponse = httpClient.execute(request, addCookieToContext(request, fusionSession, user));
        } else {
            httpResponse = httpClient.execute(request);
        }

        String json = IOUtils.toString(httpResponse.getEntity().getContent());
        if (httpResponse.getStatusLine().getStatusCode() == 200) {
            return json;
        }

        throw new IOException(json);
    }

    public void close() throws IOException {
        httpClient.close();
    }

    private HttpClientContext addCookieToContext(HttpGet request, FusionSession fusionSession, User user) {
        HttpClientContext httpContext = null;
        Cookie cookie = fusionSession.getCookie();

        if (cookie != null) {
            if (cookie.getDomain() == null) {
                BasicClientCookie cookieWithDomain = new BasicClientCookie(cookie.getName(), cookie.getValue());
                cookieWithDomain.setPath(cookie.getPath());
                cookieWithDomain.setSecure(cookie.isSecure());
                cookieWithDomain.setDomain(request.getURI().getHost());
                cookie = cookieWithDomain;
            }

            logger.trace("Valid Fusion session cookie found for user {}", user.getId());

            final CookieStore cookieStore = new BasicCookieStore();
            cookieStore.addCookie(cookie);

            List<Header> headers = new DefaultCookieSpec().formatCookies(Collections.singletonList(cookie));
            for (Header header : headers) {
                request.setHeader(header);
            }

            httpContext = HttpClientContext.create();
            httpContext.setCookieStore(cookieStore);
            httpContext.setAttribute(HttpClientContext.COOKIE_STORE, cookieStore);
        }

        return httpContext;
    }
}
