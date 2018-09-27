package twigkit.fusion;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import org.codehaus.jettison.json.JSONArray;
import twigkit.http.util.HttpClientFactory;
import twigkit.security.SecurityProvider;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.util.List;

/**
 * Security-backed configuration resource
 *
 * @author scottbrown
 */
@Singleton
@Path("/secure/setup")
public class SecureFusionConfigurationResource extends ConfigurationResource {

    @Inject
    private SecurityProvider securityProvider;

    @GET
    @Path("/query-profiles")
    @Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public Response queryProfiles(@QueryParam("app") String app) throws Exception {
        final String response = new FusionClient(HttpClientFactory.get()).request(getQueryProfilesEndpoint(app), securityProvider.getUser());
        final List<String> fusionQueryProfileIds = objectsToIds(new JSONArray(response));

        if (fusionQueryProfileIds != null) {
            return Response.ok(fusionQueryProfileIds).build();
        }

        return Response.serverError().build();
    }
}
