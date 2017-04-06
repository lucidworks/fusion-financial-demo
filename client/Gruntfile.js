'use strict';

module.exports = function (grunt) {

  // Load grunt tasks automatically
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  require('time-grunt')(grunt);

  grunt.loadNpmTasks('grunt-connect-proxy');
  var modRewrite = require('connect-modrewrite');

  // Configurable paths for the application
  var appConfig = {
    app: 'src/main/',
    dist: 'target-grunt/app/'
  };

  // Define the configuration for all the tasks
  grunt.initConfig({

    // Project settings
    yeoman: appConfig,

    // Watches files for changes and runs tasks based on the changed files
    watch: {
      bower: {
        files: ['bower.json'],
        tasks: ['wiredep']
      },
      js: {
        files: ['<%= yeoman.app %>/scripts/{,*/}*.js'],
        //tasks: ['newer:jshint:all'],
        options: {
          livereload: '<%= connect.options.livereload %>'
        }
      },
      jsTest: {
        files: ['test/spec/{,*/}*.js'],
        tasks: ['karma']
      },
      styles: {
        files: ['<%= yeoman.app %>/styles/{,*/}*.css'],
        tasks: ['newer:copy:styles', 'autoprefixer']
      },
      gruntfile: {
        files: ['Gruntfile.js']
      },
      livereload: {
        options: {
          livereload: '<%= connect.options.livereload %>'
        },
        files: [
          '<%= yeoman.app %>/{,*/}*.html',
          '.tmp/styles/{,*/}*.css',
          '<%= yeoman.app %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
        ]
      },
      less: {
        files: ['<%= yeoman.app %>/less/{,*/}*.less'],
        tasks: ['compile-less']
      }
    },

    // The actual grunt server settings
    connect: {
      options: {
        port: 9000,
        // Change this to '0.0.0.0' to access the server from outside.
        hostname: 'localhost',
        // livereload: false
        livereload: 35729 // uncomment to enable livereload
      },
      proxies: [
        {
          context: '/twigkit/api',
          host: 'localhost',
          port: 8080,
          xforward: false,
          ws: true
        }
      ],
      livereload: {
        options: {
          // livereload: false,
          livereload: true, // uncomment to enable livereload
          open: true,
          middleware: function (connect) {
            return [
              require('grunt-connect-proxy/lib/utils').proxyRequest,
              modRewrite(['^[^\\.]*$ /index.html [L]']),
              connect.static('.tmp'),
              connect().use(
                '/bower_components',
                connect.static('./bower_components')
              ),
              connect.static(appConfig.app)
            ];
          }
        }
      }
    },

    // Empties folders to start fresh
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            '.tmp',
            '<%= yeoman.dist %>/{,*/}*',
            '!<%= yeoman.dist %>/.git{,*/}*'
          ]
        }]
      },
      server: '.tmp'
    },

    // Automatically inject Bower components into the app
    wiredep: {
      app: {
        src: ['<%= yeoman.app %>/index.html'],
        ignorePath: new RegExp('(\.\./)*') ///\.\.\//
      },
      wro: {
        src: ['<%= yeoman.app %>/webapp/WEB-INF/wro.xml'],
        ignorePath: new RegExp('(\.\./)*'), ///\.\.\//
        fileTypes: {
          xml: {
            block: /(([ \t]*)<!--\s*bower:*(\S*)\s*-->)(\n|\r|.)*?(<!--\s*endbower\s*-->)/gi,
            detect: {
              js: /<script.*src=['"]([^'"]+)/gi,
              css: /<link.*href=['"]([^'"]+)/gi
            },
            replace: {
              js: '<js>classpath:/generated/scripts/{{filePath}}</js>',
              css: '<css>classpath:/generated/styles/{{filePath}}</css>'
            }
          }
        }
      }
    },

    // Reads HTML for usemin blocks to enable smart builds that automatically
    // concat, minify and revision files. Creates configurations in memory so
    // additional tasks can operate on them
    useminPrepare: {
      html: '<%= yeoman.app %>/index.html',
      options: {
        dest: '<%= yeoman.dist %>',
        flow: {
          html: {
            steps: {
              js: ['concat', 'uglifyjs'],
              //css: ['concat']
              css: ['cssmin']
            },
            post: {}
          }
        }
      }
    },

    // Performs rewrites using the useminPrepare configuration
    usemin: {
      html: ['<%= yeoman.dist %>/{,*/}*.html'],
      css: ['<%= yeoman.dist %>/styles/{,*/}*.css'],
      options: {
        assetsDirs: [
          '<%= yeoman.dist %>',
          '<%= yeoman.dist %>/images',
          '<%= yeoman.dist %>/styles'
        ]
      }
    },

    // The following *-min tasks will produce minified files in the dist folder
    // By default, your `index.html`'s <!-- Usemin block --> will take care of
    // minification. These next options are pre-configured if you do not wish
    // to use the Usemin blocks.
    cssmin: {
      dist: {
        options: {
          advanced: false,
          restructuring: false
        },
        files: {
          '<%= yeoman.dist %>/styles/main.css': [
            '.tmp/styles/{,*/}*.css'
          ]
        }
      }
    },

    // Copies remaining files to places other tasks can use
    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            '*.html',
            'views/{,*/}*.html',
            'images/{,*/}*.{webp}',
            'styles/fonts/{,*/}*.*',
            'assets/*'
          ]
        }, {
          expand: true,
          cwd: '.tmp/images',
          dest: '<%= yeoman.dist %>/images',
          src: ['generated/*']
        }]
      },
      styles: {
        expand: true,
        cwd: '<%= yeoman.app %>/styles',
        dest: '.tmp/styles/',
        src: '{,*/}*.css'
      }
    },

    // Run some tasks in parallel to speed up the build process
    concurrent: {
      server: [
        'copy:styles'
      ],
      dist: [
        'copy:styles'
      ]
    },

    less: {
      development: {
        files: {
          '<%= yeoman.app %>/styles/twigkit.css': '<%= yeoman.app %>/less/twigkit.less'
        }
      },
      production: {
        options: {
          plugins: [
            // Add vendor prefixes to compiled CSS
            new (require('less-plugin-autoprefix'))({browsers: ["last 3 versions"]})
          ]
        },
        files: {
          '<%= yeoman.app %>/styles/twigkit.css': '<%= yeoman.app %>/less/twigkit.less'
        }
      }
    },

    // ng-annotate tries to make the code safe for minification automatically
    // by using the Angular long form for dependency injection.
    ngAnnotate: {
      dist: {
        files: [{
          expand: true,
          cwd: '.tmp/concat/scripts',
          src: '*.js',
          dest: '.tmp/concat/scripts'
        }]
      }
    }

  });

  // Register tasks

  // Compile then start a connect web server
  grunt.registerTask('serve', [
    'clean:server',
    'wiredep',
    'concurrent:server',
    'configureProxies:server',
    'connect:livereload',
    'watch'
  ]);

  grunt.registerTask('build', [
    //'clean:dist', // Empty dist folders
    //'wiredep', // Add bower dependencies to index.html
    'wiredep:wro' // Add bower dependencies to wro.xml
    //'less', // Compile LESS and add vendor prefixes
    //'useminPrepare', // Prepare minifier
    //'concurrent:dist', // Copy styles to correct place
    //'concat', // Concatenate JS files
    //'ngAnnotate', // Allow JS to be minified safely
    //'copy:dist' // Copy files to dist
    //'cssmin:dist', // Minify CSS in dist folder
    //'uglify', // Uglify JS in dist
    //'usemin' // Run minifier
  ]);

  grunt.registerTask('compile-less', [
    'less',
    'useminPrepare',
    'concurrent:dist',
    'cssmin:dist',
    'usemin'
  ]);

  grunt.registerTask('default', ['build']);
};
