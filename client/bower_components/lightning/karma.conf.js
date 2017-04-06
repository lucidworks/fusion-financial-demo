// Karma configuration
// Generated on Mon May 11 2015 14:59:10 GMT+0100 (BST)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],

    files: [
      'bower_components/jquery/jquery.js',
      'bower_components/angular/angular.js',
      'bower_components/angular-sanitize/angular-sanitize.js',
      'bower_components/angular-cookies/angular-cookies.js',
      'bower_components/angular-mocks/angular-mocks.js',
      'bower_components/angular-animate/angular-animate.js',
      'http://maps.googleapis.com/maps/api/js?libraries=visualization&language=en',
      'http://ecn.dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=7.0',
      'bower_components/angular-websocket/dist/angular-websocket.js',
      'bower_components/angular-relative-date/dist/angular-relative-date.js',
      'bower_components/highcharts/highstock.js',
      'bower_components/highcharts/highcharts-more.js',
      'bower_components/highcharts/modules/exporting.js',
      'bower_components/highcharts/modules/solid-gauge.js',
      'bower_components/highcharts-ng/dist/highcharts-ng.js',
      'bower_components/hammerjs/hammer.min.js',
      'bower_components/ngstorage/ngStorage.min.js',
      'bower_components/lodash/dist/lodash.min.js',
      'bower_components/angular-simple-logger/dist/angular-simple-logger.min.js',
      'bower_components/angular-google-maps/dist/angular-google-maps.min.js',
      'bower_components/angular-bing-maps/dist/angular-bing-maps.min.js',
      'bower_components/angular-esri-map/dist/angular-esri-map.min.js',
      'bower_components/angularjs-slider/dist/rzslider.js',
      'src/app.js', 'src/directives/**/*.js', 'src/filters/**/*.js', 'src/services/**/*.js',
      'test/testScope.js', 'test/spec/**/*.js'
    ],

    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'src/**/*.js': ['coverage']
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage'],

    // optionally, configure the reporter
    coverageReporter: {
      dir: 'coverage/',
      reporters: [
        // reporters not supporting the `file` property
        { type: 'html', subdir: 'results' },
      ]
    },

    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS2'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
