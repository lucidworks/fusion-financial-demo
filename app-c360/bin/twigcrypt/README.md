## Twigcrypt value encryption utility

This utility is designed to allow you to quickly encrypt sensitive string values at the command line. It uses the framework's internal two-way encryption mechanism so anywhere in the code this is used the value can be decrypted. See ConfigurationEncryptor in Framework for more details.

To encrypt a value such as a configured password run the following (note the single quotes around yourSensitiveValue):

```
./twigcrypt.sh yourSecretSeed 'yourSensitiveValue'
```

This will output an encrypted string. You must copy this (the whole string) and paste into your config file e.g. in your platforms conf add:

```
username:jbloggs
password:Enc(ABC123==)
```

Then you must also configure the seed in the application's security configuration under .../conf/security/security.conf:

```
password: yourSecretSeed
```

As long as ConfigurationEncryptor is invoked to decrypt the value in the code in which this config parameter is used, it will be decrypted back to plain text at the point of use.

This avoids ever storing or outputting sensitive configuration values in plain text

NOTE: Please use a secure randomly generated *alphanumeric* seed (special characters can cause problems). Security best practice must be followed to update the seed and encrypted values.
