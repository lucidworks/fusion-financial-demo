#Twigkit Lightning

Twigkit Lightning is a single-page JavaScript framework that supports the same syntax and ease of development for complex business applications as our traditional JSP tag library and supporting services. It is however a simpler way of developing and managing applications since no runtime other than the browser is required for development or deployment.

This redesigned framework represents years of learning in the space where data is requested and rendered as and when it is needed for best-of-breed richness and performance.

## Documentation  
Lightning documentation can be loaded by doing the following.
 - Clone the project
 - Navigate to the project within your terminal
 - `npm install` you may need to prefix with sudo
 - `bower install`
 - `grunt`
 - `grunt docs`
 - This should then open up the documentation within your browser.
 
## Local Development
For developing lightning locally there are a few things you need to do.

- Fork a copy of lightning and clone it to your machine. `git clone FORKED_REPOSITORY.git`
- Open the directory within the command line and run `npm install` you may need to prefix with sudo and then `bower install`
- Now you should be able to run `grunt` and see the tests running.
- Within the command line type `bower link` this will register your local version of lightning and ready to link to other projects so that they use your local version.
- Enter `grunt watch:scripts` in the command line, this will watch for any changes and rebuild lightning when they happen.
- In a new terminal window navigate to a project using Lighting and enter `bower link lightning` this should link this project to your local copy of lightning.

Now any changes you make will be built and then can be seen when running applications your local lightning is linked to.

## Versions
Versions 0.1.0 Supports Twigkit 3.0-M3 and lower. If you are using a version of Twigkit higher than 3.0-M3 you will need to set the version in your bower.json file to be 0.1.1 or greater.

## Release process

In order to release a version of lightning you must do the following.

Firstly create an access token with "Full control of private repositories".
https://help.github.com/articles/creating-an-access-token-for-command-line-use/

Then add the access token to the environment variable `GITHUB_ACCESS`

In your terminal cd to your local copy of lightning and make sure your on the master branch.
```
git checkout master
```
Make sure this branch is up-to-date:
```
git fetch upstream
git merge upstream/master
```
Run the following command to release depending on the version number to be released.
```
grunt release:patch //(0.1.1 to 0.1.2)
grunt release:minor //(0.1.1 to 0.2.0)
grunt release:major //(0.1.1 to 1.0.0)
```

You can add `--no-write` to test the version you are releasing is correct.
