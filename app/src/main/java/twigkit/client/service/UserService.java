package twigkit.client.service;


import com.google.inject.Inject;
import org.codehaus.jettison.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.conf.ConfiguredPlatformProvider;
import twigkit.model.Filter;
import twigkit.model.Query;
import twigkit.platform.Platform;
import twigkit.service.TwigKitService;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.StreamingOutput;
import java.io.OutputStream;

@Path(UserService.ENTRY_PATH)
public class UserService implements TwigKitService {

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    public static final String ENTRY_PATH = "/user-profile";

    @Inject
    private ConfiguredPlatformProvider platformProvider;

    @GET
    @Path("/{username}/")
    @Produces({MediaType.APPLICATION_OCTET_STREAM})
    public Response get(@PathParam("username") String username) {
        Platform userPrefsPlatform = platformProvider.get("platforms.fusion.finance.user-prefs");


        Query userQuery = new Query();
        userQuery.setResultsPerPage(1);
        userQuery.addFilter(new Filter("_lw_data_source_s", "user-prefs"));
        userQuery.addFilter(new Filter("username_s", username.toLowerCase()));

        twigkit.model.Response response = userPrefsPlatform.search(userQuery);

        final String responseBody = new JSONObject(response.getResults().get(0).getFields()).toString();
        logger.info(responseBody);

        try {
            StreamingOutput streamingOutput = (OutputStream outputStream) -> {
                outputStream.write(responseBody.getBytes());
                outputStream.flush();
            };
            return Response.ok(streamingOutput, MediaType.APPLICATION_OCTET_STREAM)
                    .status(Response.Status.OK)
                    .build();
        } catch (Exception e) {
            logger.error("Error streaming image", e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).build();
        }
    }
}
