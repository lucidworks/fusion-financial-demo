package twigkit.client.service;


import com.google.inject.Inject;
import org.codehaus.jettison.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.fig.Config;
import twigkit.fig.Fig;
import twigkit.service.TwigKitService;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.StreamingOutput;
import java.io.OutputStream;

@Path(ConfigService.ENTRY_PATH)
public class ConfigService implements TwigKitService {

    private static final Logger logger = LoggerFactory.getLogger(ConfigService.class);
    public static final String ENTRY_PATH = "/app-config";

    @Inject
    private Fig fig;

    @GET
    @Path("/")
    @Produces({MediaType.APPLICATION_OCTET_STREAM})
    public Response get() {
        Config config = fig.get("app-config-private");

        String configJson = "";
        if (config != null) {
            configJson = new JSONObject(config.map()).toString();
        }

        try {
            String finalConfigJson = configJson;
            StreamingOutput streamingOutput = (OutputStream outputStream) -> {
                outputStream.write(finalConfigJson.getBytes());
                outputStream.flush();
            };
            return Response.ok(streamingOutput, MediaType.APPLICATION_OCTET_STREAM)
                    .status(Response.Status.OK)
                    .build();
        } catch (Exception e) {
            logger.error("Error streaming config", e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).build();
        }
    }
}
