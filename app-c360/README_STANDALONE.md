Welcome to App Studio
=====================

We believe creating search applications shouldn't be overwhelming, so we created App Studio to help you build modern, user-friendly search apps quickly and simply.

Getting Started
===============

With App Studio you can build a mobile-ready search application in a matter of minutes. When you run App Studio for the first time you will be guided through the configuration of your application, from connecting to a data source to customizing how your search results should be presented. At the end of the process you have a single-page search interface displaying data from your Fusion collection, complete with faceted navigation, type-ahead suggestions and more.

For more information, see the documentation at https://doc.lucidworks.com/app-studio/4.0/



Starting and Stopping
--------------------------------

### Linux, Mac OS X

To start the application, run the following command from a terminal:

- `./app-studio.sh start`

To stop the application, run the following command from a terminal:

- `./app-studio.sh stop`

### Windows

Initial setup: From an Administrator-level Powershell prompt, run `Set-ExecutionPolicy unrestricted`.  Note that this only needs to be performed once, and will allow Powershell scripts to be executed.

To start the application, run the following command from a command prompt:

- `app-studio-start.bat`

Alternatively, double-click on the `app-studio-start.bat` file.

To stop the application, run the following command from a Powershell command prompt:

- `app-studio-stop.bat`

Alternatively, double-click on the `app-studio-stop.bat` file.


Accessing App Studio
--------------------

Once started, the application is served up at `http://localhost:8080`. You will be asked to authenticate, for which you can use any of your Fusion "native realm" users, or the realm that can be optionally configured in the `config/security/fusion.conf` file.


License
-------

App Studio comes with a 30-day license key in `twigkit.lic`. Once this expires, contact Lucidworks for a new license: https://lucidworks.com/company/contact/


Advanced Configuration
======================

Running the app over SSL
------------------------

The webapp can also be served over HTTPS using SSL encryption. This is done using the following parameters when invoking the startup scripts:

- `-Dtwigkit.ssl=true` required to turn on secure mode

We include a keystore file with a default self-signed key for development / testing of secure mode. However in order to establish proper trust you will need to import your own valid SSL certificate into the file `keystore.jks` or create your own keystore file. You can then configure SSL via:

- `-Dtwigkit.https.port` optionally sets the HTTPS port (defaults to 8765)
- `-Dtwigkit.http.port` optionally sets the HTTP port (defaults to 8080)
- `-Dtwigkit.keystore.file` keystore filename / location relative to webapp (defaults to 'keystore.jks')
- `-Dtwigkit.keystore.password` password to the keystore (defaults to 'p4ssw0rd')
- `-Dtwigkit.keystore.alias` name of the key in the keystore to be used (defaults to 'default-key')
