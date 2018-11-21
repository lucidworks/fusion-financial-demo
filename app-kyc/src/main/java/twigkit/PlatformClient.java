package twigkit;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;

public abstract class PlatformClient {

    /**
     * Utility for checking if a platform responds.
     *
     * @param host
     * @param port
     * @return
     * @throws Exception
     */
    public static boolean ping(String host, int port) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), 500);
            return true;
        } catch (IOException e) {
            return false;
        }
    }
}
