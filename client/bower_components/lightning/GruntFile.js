module.exports = function (grunt) {

    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-ngdocs');
    grunt.loadNpmTasks('grunt-contrib-connect');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-open');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-release');
    grunt.loadNpmTasks('grunt-exec');

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        karma: {
            options: {
                configFile: 'karma.conf.js',
                singleRun: true,
                browserNoActivityTimeout: 60000,
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
                    'bower_components/angular-relative-date/dist/angular-relative-date.js'
                ]
            },
            unit: {
                configFile: 'karma.unit.conf.js',
                files: [
                    {
                        src: [
                            'bower_components/highcharts/js/highstock.js',
                            'bower_components/highcharts/js/highcharts-more.js',
                            'bower_components/highcharts/js/modules/exporting.js',
                            'bower_components/highcharts/js/modules/solid-gauge.js',
                            'bower_components/highcharts/js/modules/map.js',
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
                            'test/testScope.js',
                            'test/spec/**/*.js'
                        ]
                    }
                ]
            },
            dist: {
                files: [
                    {
                        src: [
                            'dist/lightning.min.js',
                            'test/testScope.js',
                            'test/spec/**/*.js']
                    }
                ]
            }
        },
        concat: {
            options: {
                separator: '\n\n'
            },
            dist: {
                files: {
                    'dist/lightning.maps.google.vendor.js':[
                        'bower_components/lodash/dist/lodash.min.js',
                        'bower_components/angular-simple-logger/dist/angular-simple-logger.min.js',
                        'bower_components/angular-google-maps/dist/angular-google-maps.min.js'
                    ],
                    'dist/lightning.maps.esri.vendor.js':[
                        'bower_components/angular-esri-map/dist/angular-esri-map.min.js'
                    ],
                    'dist/lightning.maps.bing.vendor.js': [
                        'bower_components/angular-bing-maps/dist/angular-bing-maps.min.js'
                    ],
                    'dist/lightning.maps.vendor.js':[
                        'dist/lightning.maps.google.vendor.js',
                        'dist/lightning.maps.esri.vendor.js',
                        'dist/lightning.maps.bing.vendor.js'
                    ],
                    'dist/lightning.visualisations.highcharts.vendor.js': [
                        'bower_components/highcharts/js/highstock.js',
                        'bower_components/highcharts/js/highcharts-more.js',
                        'bower_components/highcharts/highcharts-3d.js',
                        'bower_components/highcharts/js/modules/exporting.js',
                        'bower_components/highcharts/js/modules/solid-gauge.js',
                        'bower_components/highcharts/js/modules/map.js',
                        'bower_components/highcharts-ng/dist/highcharts-ng.js',
                        'bower_components/angular-websocket/dist/angular-websocket.js'
                    ],
                    'dist/lightning.visualisations.other.vendor.js': [
                        'bower_components/angularjs-slider/dist/rzslider.js'
                    ],
                    'dist/lightning.visualisations.vendor.js':[
                        'dist/lightning.visualisations.highcharts.vendor.js',
                        'dist/lightning.visualisations.other.vendor.js'
                    ],
                    'dist/lightning.core.js': [
                        'bower_components/moment/min/moment.min.js',
                        'bower_components/ngstorage/ngStorage.min.js',
                        'bower_components/angular-relative-date/dist/angular-relative-date.js',
                        'bower_components/hammerjs/hammer.min.js',
                        'bower_components/lodash/dist/lodash.min.js',
                        'src/app.js',
                        'src/directives/**/*.js',
                        'src/filters/**/*.js',
                        'src/services/**/*.js',
                        '!src/directives/visualisations/geo/*.js',
                        '!src/directives/visualisations/charts/**/*.js'
                    ],
                    'dist/lightning.maps.core.js': [
                        'src/directives/visualisations/geo/geoMap.js',
                        'src/directives/visualisations/geo/geoLayer.js'
                    ],
                    'dist/lightning.maps.google.js': [
                        'src/directives/visualisations/geo/heatmap.js'
                    ],
                    'dist/lightning.maps.esri.js': [
                        'src/directives/visualisations/geo/esriHeatmap.js',
                        'src/directives/visualisations/geo/esriWebmap.js'
                    ],
                    'dist/lightning.maps.js': [
                        'dist/lightning.maps.core.js',
                        'dist/lightning.maps.google.js',
                        'dist/lightning.maps.esri.js'
                    ],
                    'dist/lightning.visualisations.highcharts.js': [
                        'src/directives/visualisations/charts/highcharts/*.js'
                    ],
                    'dist/lightning.visualisations.other.js': [
                        'src/directives/visualisations/charts/*.js'
                    ],
                    'dist/lightning.visualisations.js': [
                        'dist/lightning.visualisations.highcharts.js',
                        'dist/lightning.visualisations.other.js'
                    ],
                    'dist/lightning.js': [
                        'dist/lightning.maps.vendor.js',
                        'dist/lightning.visualisations.vendor.js',
                        'dist/lightning.core.js',
                        'dist/lightning.visualisations.js',
                        'dist/lightning.maps.js'
                    ]
                }
            },
            // Used to quickly build for development
            fast: {
                files: {
                    'dist/lightning.maps.google.vendor.min.js':[
                        'bower_components/lodash/dist/lodash.min.js',
                        'bower_components/angular-simple-logger/dist/angular-simple-logger.min.js',
                        'bower_components/angular-google-maps/dist/angular-google-maps.min.js'
                    ],
                    'dist/lightning.maps.esri.vendor.min.js':[
                        'bower_components/angular-esri-map/dist/angular-esri-map.min.js'
                    ],
                    'dist/lightning.maps.bing.vendor.min.js': [
                        'bower_components/angular-bing-maps/dist/angular-bing-maps.min.js'
                    ],
                    'dist/lightning.maps.vendor.min.js':[
                        'dist/lightning.maps.google.vendor.js',
                        'dist/lightning.maps.esri.vendor.js',
                        'dist/lightning.maps.bing.vendor.js'
                    ],
                    'dist/lightning.visualisations.highcharts.vendor.min.js': [
                        'bower_components/highcharts/js/highstock.js',
                        'bower_components/highcharts/js/highcharts-more.js',
                        'bower_components/highcharts/highcharts-3d.js',
                        'bower_components/highcharts/js/modules/exporting.js',
                        'bower_components/highcharts/js/modules/solid-gauge.js',
                        'bower_components/highcharts/js/modules/map.js',
                        'bower_components/highcharts-ng/dist/highcharts-ng.js',
                        'bower_components/angular-websocket/dist/angular-websocket.js'
                    ],
                    'dist/lightning.visualisations.other.vendor.min.js': [
                        'bower_components/angularjs-slider/dist/rzslider.js'
                    ],
                    'dist/lightning.visualisations.vendor.min.js':[
                        'dist/lightning.visualisations.highcharts.vendor.js',
                        'dist/lightning.visualisations.other.vendor.js'
                    ],
                    'dist/lightning.core.min.js': [
                        'bower_components/moment/min/moment.min.js',
                        'bower_components/ngstorage/ngStorage.min.js',
                        'bower_components/angular-relative-date/dist/angular-relative-date.js',
                        'bower_components/hammerjs/hammer.min.js',
                        'src/app.js',
                        'src/directives/**/*.js',
                        'src/filters/**/*.js',
                        'src/services/**/*.js',
                        '!src/directives/visualisations/geo/*.js',
                        '!src/directives/visualisations/charts/**/*.js'
                    ],
                    'dist/lightning.maps.core.min.js': [
                        'src/directives/visualisations/geo/geoMap.js',
                        'src/directives/visualisations/geo/geoLayer.js'
                    ],
                    'dist/lightning.maps.google.min.js': [
                        'src/directives/visualisations/geo/heatmap.js'
                    ],
                    'dist/lightning.maps.esri.min.js': [
                        'src/directives/visualisations/geo/esriHeatmap.js',
                        'src/directives/visualisations/geo/esriWebmap.js'
                    ],
                    'dist/lightning.maps.min.js': [
                        'dist/lightning.maps.core.js',
                        'dist/lightning.maps.google.min.js',
                        'dist/lightning.maps.esri.min.js'
                    ],
                    'dist/lightning.visualisations.highcharts.min.js': [
                        'src/directives/visualisations/charts/highcharts/*.js'
                    ],
                    'dist/lightning.visualisations.other.min.js': [
                        'src/directives/visualisations/charts/*.js'
                    ],
                    'dist/lightning.visualisations.min.js': [
                        'dist/lightning.visualisations.highcharts.min.js',
                        'dist/lightning.visualisations.other.min.js'
                    ],
                    'dist/lightning.min.js': [
                        'dist/lightning.maps.vendor.js',
                        'dist/lightning.visualisations.vendor.js',
                        'dist/lightning.core.min.js',
                        'dist/lightning.visualisations.min.js',
                        'dist/lightning.maps.min.js'
                    ]
                }
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                files: {
                    'dist/lightning.maps.bing.vendor.min.js':['dist/lightning.maps.bing.vendor.js'],
                    'dist/lightning.maps.esri.vendor.min.js':['dist/lightning.maps.esri.vendor.js'],
                    'dist/lightning.maps.google.vendor.min.js':['dist/lightning.maps.google.vendor.js'],
                    'dist/lightning.maps.vendor.min.js':['dist/lightning.maps.vendor.js'],
                    'dist/lightning.visualisations.highcharts.vendor.min.js':['dist/lightning.visualisations.highcharts.vendor.js'],
                    'dist/lightning.visualisations.other.vendor.min.js':['dist/lightning.visualisations.other.vendor.js'],
                    'dist/lightning.visualisations.vendor.min.js':['dist/lightning.visualisations.vendor.js'],
                    'dist/lightning.core.min.js': ['dist/lightning.core.js'],
                    'dist/lightning.visualisations.highcharts.min.js': ['dist/lightning.visualisations.highcharts.js'],
                    'dist/lightning.visualisations.other.min.js': ['dist/lightning.visualisations.other.js'],
                    'dist/lightning.visualisations.min.js': ['dist/lightning.visualisations.js'],
                    'dist/lightning.maps.core.min.js': ['dist/lightning.maps.core.js'],
                    'dist/lightning.maps.google.min.js': ['dist/lightning.maps.google.js'],
                    'dist/lightning.maps.esri.min.js': ['dist/lightning.maps.esri.js'],
                    'dist/lightning.maps.min.js': ['dist/lightning.maps.js'],
                    'dist/lightning.min.js': ['dist/lightning.js']
                }
            }
        },
        watch: {
            scripts: {
                files: ['src/app.js', 'src/directives/**/*.js', 'src/filters/**/*.js', 'src/services/**/*.js'],
                tasks: ['concat:dist', 'uglify', 'jshint', 'ngdocs', 'karma:dist']
            },
            fast: {
                files: ['src/app.js', 'src/directives/**/*.js', 'src/filters/**/*.js', 'src/services/**/*.js'],
                tasks: ['concat:fast']
            }
        },
        ngdocs: {
            options: {
                dest: 'docs',
                editLink: false,
                editExample: false,
                html5Mode: false,
                scripts: [
                    'bower_components/angular/angular.js',
                    'bower_components/angular-animate/angular-animate.js',
                    'bower_components/angular-sanitize/angular-sanitize.js',
                    'bower_components/angular-cookies/angular-cookies.js',
                    'dist/lightning.js',
                    'dist/lightning.min.js',
                    'docs-assets/colonDashCaseFilter.js',
                    'docs-assets/custom-docs.js'
                ],
                styles: [
                    'bower_components/phoenix/demo/styles/phoenix.all.css',
                    'docs-assets/overrides.css',
                    'docs-assets/prettify-theme.css',
                    'docs-assets/custom.bootstrap.css',
                    'docs-assets/logo.png',
                    'docs-assets/blue_marker.png',
                    'docs-assets/tk-cambridge-marker.png',
                    'docs-assets/tk-london-marker.png',
                    'docs-assets/user-defined-template.tmp.html',
                    'docs-assets/level1.tpl.html',
                    'docs-assets/level2.tpl.html',
                    'docs-assets/level3.tpl.html',
                    'docs-assets/favicon.ico',
                    'docs-assets/twigkit-logo-red-s.png'
                ],
                template: 'docs-assets/index.tmp.html'
            },
            api: {
                src: ['src/**/*.js', 'docs-assets/index.ngdoc'],
                title: 'Reference'
            }
        },
        connect: {
            docs: {
                options: {
                    keepalive: true,
                    hostname: 'localhost',
                    port: 8011,
                    base: 'docs',
                    open: true
                }
            }
        },
        open: {
            coverage: {
                path: 'coverage/results/index.html'
            }
        },
        clean: ['docs'],

        jshint: {
            options: {
                jshintrc: '<%= baseDir %>.jshintrc',
                reporterOutput: ""
            },
            all: ['src/app.js', 'src/directives/**/*.js', 'src/filters/**/*.js', 'src/services/**/*.js']
        },

        release: {
            options: {
                additionalFiles: ['bower.json'],
                npm: false,
                github: {
                    repo: 'twigkit/lightning', //put your user/repo here
                    accessTokenVar: 'GITHUB_ACCESS', //ENVIRONMENT VARIABLE that contains GitHub Access Token
                },
            }
        },

        exec: {
            changelog: {
                cmd: 'github_changelog_generator twigkit/lightning'
            },
            changelogAdd:{
                cmd: 'git add .'
            },
            changelogCommit:{
                cmd: 'git commit -m "Changelog"'
            },
            changelogPush:{
                cmd: 'git push'
            }
        }
    });

    // Default task(s).
    grunt.registerTask('default', ['concat:dist', 'uglify', 'jshint', 'ngdocs', 'karma:dist']);

    grunt.registerTask('test', [
        'karma:unit'
    ]);

    grunt.registerTask('docs', ['clean', 'ngdocs', 'connect:docs']);

    grunt.registerTask('coverage', ['karma:unit', 'open']);

    grunt.registerTask('build', ['concat:dist', 'uglify']);
    grunt.registerTask('fast', ['concat:fast']);

    grunt.registerTask('changelog',['exec:changelog']);

    grunt.registerTask('changelogCommit',['exec:changelog','exec:changelogAdd','exec:changelogCommit','exec:changelogPush']);
};