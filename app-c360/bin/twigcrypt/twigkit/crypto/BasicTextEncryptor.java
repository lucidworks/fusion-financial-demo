package twigkit.crypto;

/**
 * Description of this class.
 *
 * @author bjarkih
 */
public class BasicTextEncryptor implements TextEncryptor {

    protected org.jasypt.util.text.BasicTextEncryptor encryptor;

    public BasicTextEncryptor(String password) {
        this.encryptor = new org.jasypt.util.text.BasicTextEncryptor();
        this.encryptor.setPassword(password);
    }

    @Override
    public String encrypt(String message) {
        return encryptor.encrypt(message);
    }

    @Override
    public String decrypt(String encryptedMessage) {
        return encryptor.decrypt(encryptedMessage);
    }
}
