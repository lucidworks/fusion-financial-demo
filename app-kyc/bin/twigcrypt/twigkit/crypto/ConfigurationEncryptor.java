package twigkit.crypto;

import com.google.inject.*;

/**
 * Simple two-way encryption utility that delegates to bound TextEncryptor.
 * Contains main method for running at command line in order to generate encrypted values.
 *
 * Where needed this class can be injected into code that reads sensitive config values to
 * decrypt them and if they have the encryption marker [e.g. 'Enc(123abc)'] they
 * will be decrypted, otherwise [e.g. '123abc'] they will be returned as they are.
 * @author Stewart Sims
 */
public class ConfigurationEncryptor implements TextEncryptor {
    @Inject
    private TextEncryptor textEncryptor;

    @Override
    public String encrypt(String message) {
        return "Enc(" + textEncryptor.encrypt(message) + ")";
    }

    @Override
    public String decrypt(String encryptedMessage) {
        if (encryptedMessage.startsWith("Enc(") && encryptedMessage.endsWith(")")) {
            return textEncryptor.decrypt(encryptedMessage.substring(4, encryptedMessage.length()-1));
        }
        return encryptedMessage;
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Incorrect number of parameters supplied. Usage should be:");
            System.out.println("(command) yourRandomSeed yourValueToEncrypt");
        } else {
            Injector injector = Guice.createInjector(new Module() {
                @Override
                public void configure(Binder binder) {
                    binder.bind(TextEncryptor.class).toInstance(new BasicTextEncryptor(args[0]));
                }
            });
            System.out.println(injector.getInstance(ConfigurationEncryptor.class).encrypt(args[1]));
        }
    }
}
