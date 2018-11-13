package twigkit.app.inspection.ws;

import com.google.inject.Inject;
import org.codehaus.jettison.json.JSONObject;
import twigkit.app.inspection.service.AppTitleService;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

/**
 * Web service to get the host of fusion
 *
 * @author KieranDotCo
 */
@Path(AppTitleResource.SERVICE_URL)
public class AppTitleResource {


    public static final String SERVICE_URL = "/app/title";

    @Inject
    private AppTitleService appTitleService;

    /**
     * @return the fusion host from the config
     * @author KieranDotCo
     */
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response host() throws Exception {
        JSONObject response = new JSONObject();

        response.put(appTitleService.TITLE, appTitleService.getTitle());

        return Response.ok(response.toString()).build();
    }
}