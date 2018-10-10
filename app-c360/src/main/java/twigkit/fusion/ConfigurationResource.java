package twigkit.fusion;

import org.codehaus.jettison.json.JSONArray;
import org.codehaus.jettison.json.JSONException;

import java.util.ArrayList;
import java.util.List;

/**
 * Abstract class for handling REST-ful updates to configuration
 *
 * @author scottbrown
 */
public abstract class ConfigurationResource {

    public static final String APPS_ENDPOINT = "/api/apollo/apps";

    public static final String URL_SEPARATOR = "/";

    public static final String QUERY_PROFILES = "query-profiles";

    private static final String JSON_RESPONSE_KEY_ID = "id";

    protected String getQueryProfilesEndpoint(String fusionApp) {
        return APPS_ENDPOINT + URL_SEPARATOR + fusionApp.trim() + URL_SEPARATOR + QUERY_PROFILES;
    }

    /**
     * Gets a list of ids for the given list of Fusion entities.
     *
     * @param objectArray a list of Fusion entities returned from a Fusion API (e.g. apps, query profiles etc)
     * @return a list of ids for the given list of Fusion entities
     * @throws JSONException
     */
    public List<String> objectsToIds(JSONArray objectArray) throws JSONException {
        if (objectArray != null) {
            final List<String> ids = new ArrayList<>();

            for (int i = 0; i < objectArray.length(); i++) {
                ids.add(objectArray.getJSONObject(i).getString(JSON_RESPONSE_KEY_ID));
            }

            return ids;
        }

        return null;
    }
}
