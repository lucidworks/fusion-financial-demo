package twigkit.crypto;

/**
 * Identity mapping: s --> s (does no encryption).
 *
 * @author bjarkih
 */
public class IdentityMapping implements TextEncryptor {


    @Override
    public String encrypt(String message) {
        return message;
    }

    @Override
    public String decrypt(String encryptedMessage) {
        return encryptedMessage;
    }
}
