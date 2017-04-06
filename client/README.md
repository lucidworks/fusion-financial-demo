# Solr Simple Search
Twigkit makes building rich search-based applications quicker and easier than ever before. This template was built on top of a Solr search index but can be adapted for any Twigkit supported data source. This document covers:

1. [Application Overview](#application-overview)
2. [Dependencies](#dependecies)
3. [Installation](#installation)
    1. [Local Deployment](#local-deployment)
	2. [Package the web application](#package-the-web-application)

# Application Overview
Once the application is running or deployed, there will be the following key folders:
###### `src/main/webapp/static/app`
This folder contains the user interface for the web application.

###### `src/main/webapp/static/app/views`
The views folder is where the HTML pages are kept. `search.html` is the main search page. Additional pages can be created as needed.

###### `src/main/webapp/static/app/less`
The less folder contains all of the files for theming the application. These should be used instead of the css files in the styles folder as they are automatically generated from the less files.

###### `src/main/webapp/static/app/scripts/routes.js`
This file is where the URL routing can be configured. There is a default rule in place that says `/{foo}/` should use `src/main/webapp/static/app/views/{foo}.html`, hence `search` is routed to `search.html`

# Setup
Twigkit uses a combination of `node` and `bower` for managing the frontend dependencies and `grunt` for running tasks such as minifying code and compiling. Once the GitHub repository has been cloned follow the steps below to get all of the required dependencies, all commands should be ran from the project folder.
    
1. Download and install [Node](https://nodejs.org/en/download/)
2. `npm install`
3. `bower install`


# Installation
Twigkit will automatically add dependencies, compile LESS into CSS, concatenate, and minifiy javascript files ready for deployment. Enter the following command from the project folder:
    
    grunt
    

## Running Twigkit
### Local Deployment
You can run the application using the [Jetty](http://www.eclipse.org/jetty/) servlet engine and http server that ships with Maven. Enter the following command from the project folder:

	mvn clean jetty:run  -Dtwigkit.profile={aws|local}
	
For local development an additional frontend server is required for serving the user interface. Enter the following command from the project folder:

    grunt serve
    
A browser window will automatically be opened at [http://localhost:8080/](http://localhost:8080/) where the application is running.

### Package the web application

To package the web application for deployment (rather than run it locally), you can run the following command from the project folder:

	mvn clean package

This will generate a web application archive file (.war) in the `target/` folder. You can then deploy the generated package.
