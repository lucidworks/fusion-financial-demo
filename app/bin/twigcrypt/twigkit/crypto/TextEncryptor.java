package twigkit.crypto;

import com.google.inject.ImplementedBy;

/**
 * Common interface for all util classes aimed at text encryption.
 *
 * @author bjarkih
 */
@ImplementedBy(IdentityMapping.class)
public interface TextEncryptor {

    /**
     * Encrypts a message.
     *
     * @param message the message to be encrypted.
     */
    String encrypt(String message);


    /**
     * Decrypts a message.
     *
     * @param encryptedMessage the message to be decrypted.
     */
    String decrypt(String encryptedMessage);

}
