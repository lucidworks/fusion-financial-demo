package twigkit.fusion;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

/**
 * Utility class for handling general app operations
 *
 * @author scottbrown
 */
public class AppUtils {

    public static final String SUN_JAVA_COMMAND = "sun.java.command";

    /**
     * Check whether the application is running in production mode.
     *
     * @return <tt>true</tt> if the application is running in production mode.
     */
    public static Boolean isProductionMode() {
        final String appMode = System.getProperty("lucidworks.app.mode");
        return appMode != null && appMode.equals("production");
    }

    /**
     * Generates a "Fusion-aware" context path
     *
     * @param request incoming request
     * @return the context path
     */
    public static String contextPath(HttpServletRequest request) {
        return hasFusionHeaders(request) && !isAppStudio(request) ? "/webapps" + request.getContextPath() : request.getContextPath();
    }

    /**
     * Checks whether the request has any "fusion-" headers.
     *
     * @param request incoming HTTP request
     * @return <tt>true</tt> if the request contains a "fusion-" header.
     */
    public static boolean hasFusionHeaders(HttpServletRequest request) {
        Enumeration requestHeaderNames = request.getHeaderNames();

        List<String> headerNames = new ArrayList<>();
        while (requestHeaderNames.hasMoreElements()) {
            Object requestHeaderName = requestHeaderNames.nextElement();

            if (requestHeaderName instanceof String) {
                headerNames.add((String) requestHeaderName);
            }
        }

        return headerNames.stream().anyMatch(p -> p.startsWith("fusion-"));
    }

    /**
     * Check if the app is running within the App Studio context
     *
     * @param request incoming HTTP request
     * @return <tt>true</tt> if the app is running in the App Studio context.
     */
    public static boolean isAppStudio(HttpServletRequest request) {
        return request.getContextPath().equals("/app-studio");
    }

    /**
     * Check whether the app being accessed is a search app
     *
     * @return <tt>true</tt> if the app being accessed is a search app
     */
    public static boolean isSearchApp(HttpServletRequest request) {
        return Collections.list(System.getProperties().propertyNames()).stream().anyMatch(
                p -> ((String) p).startsWith("com.lucidworks"))
                && !AppUtils.isAppStudio(request);
    }

    /**
     * Check if the web app is standalone (i.e. running in an embedded Tomcat container)
     *
     * @return <tt>true</tt> if the web app is standalone
     */
    public static boolean isStandalone() {
        String sunJavaCommand = System.getProperty(SUN_JAVA_COMMAND);
        return sunJavaCommand != null && sunJavaCommand.equals("twigkit.app.embedded.App");
    }
}