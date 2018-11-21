package twigkit.fusion;

import com.google.inject.Singleton;
import org.codehaus.jettison.json.JSONArray;

import javax.ws.rs.*;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.UriInfo;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Path("/setup")
@Singleton
public class FusionConfigurationResource extends ConfigurationResource {

    public static final String HOST = "host";

    public static final String PORT = "port";

    private Map<String, FusionClient> sessions;

    public FusionConfigurationResource() {
        this.sessions = new HashMap<>();
    }

    @GET
    @Path("/realms/{host}")
    @Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public List<String> realms(@Context UriInfo uriInfo, @PathParam(HOST) String host, @QueryParam(PORT) int port) throws Exception {
        return FusionClient.realms(host, port);
    }

    @POST
    @Path("/session/{host}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public Map<String, String> session(@Context UriInfo uriInfo, @PathParam(HOST) String host, @QueryParam(PORT) int port, FusionSessionRequest request) throws Exception {
        final FusionClient client = FusionClient.session(host, port, request.getRealm(), request.getUser(), request.getPassword());
        sessions.put(client.getSessionId(), client);

        final Map<String, String> session = new HashMap<>();
        session.put("session", client.getSessionId());

        return session;
    }

    /**
     * Gets the list of Fusion apps.
     *
     * @param session value associated with cookie named id
     * @return a list of Fusion app ids
     * @throws Exception if session could not be found
     */
    @GET
    @Path("/apps")
    @Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public Response apps(@QueryParam("session") String session) throws Exception {
        FusionClient fusionClient = sessions.get(session);

        if (fusionClient != null) {
            final String response = fusionClient.request(APPS_ENDPOINT);
            final List<String> fusionAppIds = objectsToIds(new JSONArray(response));

            if (fusionAppIds != null) {
                return Response.ok(fusionAppIds).build();
            }
        } else {
            throw new Exception(String.format("No session found for %s", session));
        }

        return Response.serverError().build();
    }

    /**
     * Gets the list of query profiles for the given Fusion app.
     *
     * @param session value associated with cookie named id
     * @param app     Fusion app
     * @return a list of query profiles ids
     * @throws Exception if session could not be found
     */
    @GET
    @Path("/query-profiles")
    @Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public Response queryProfiles(@QueryParam("session") String session, @QueryParam("app") String app) throws Exception {
        FusionClient fusionClient = sessions.get(session);

        if (fusionClient != null) {
            final String response = fusionClient.request(getQueryProfilesEndpoint(app));
            final List<String> fusionQueryProfileIds = objectsToIds(new JSONArray(response));

            if (fusionQueryProfileIds != null) {
                return Response.ok(fusionQueryProfileIds).build();
            }
        } else {
            throw new Exception(String.format("No session found for %s", session));
        }

        return Response.serverError().build();
    }
}
