module.exports = function (grunt) {

    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-less-imports');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-open');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-string-replace');
    grunt.loadNpmTasks('grunt-contrib-connect');
    grunt.loadNpmTasks('grunt-express');

    grunt.initConfig({
        // create phoenix.all.less with all other less files imported in correct order
        less_imports: {
            options: {
                // import: 'once'
            },
            'src/phoenix.all.less': [
                'src/settings.less',
                'src/base/base.less',
                'src/base/base-grid.less',
                'src/base/base-grid-responsive.less',
                'src/base/base-grid-offsets.less',
                'src/base/*.less',
                'src/font/*.less',
                'src/layout/*.less',
                'src/modules/*.less',
                'src/modules/*/*.less',
                'src/colors/*.less',
                'src/utilities/*.less',
            ]
        },
        copy: {
            main: {
                files: [
                    // Copy all files from 'src' to 'dist'
                    {
                        expand: true,
                        cwd: 'src',
                        src: ['**'],
                        dest: 'dist/'
                    }
                ],
            },
        },
        less: {
            development: {
                options: {
                    plugins: [
                        // Add vendor prefixes to compiled CSS
                        new (require('less-plugin-autoprefix'))({browsers: ["last 3 versions"]})
                    ]
                },
                files: {
                    "demo/styles/phoenix.all.css": "dist/phoenix.all.less"
                }
            }
        },
        open : {
            coverage : {
                path : 'http://localhost:3000/'
            }
        },
        watch: {
            scripts: {
                files: ['**/*.less'],
                tasks: ['build']
            },
        },
        clean: ['dist'],

        // Used to replace '@import (once)' with '@import' for server side support
        'string-replace': {
            dist: {
                files: {
                    'src/phoenix.all.less': 'src/phoenix.all.less',
                },
                options: {
                    replacements: [{
                        // pattern: 'import (once)',
                        pattern: /(import \(once\))/g,
                        replacement: 'import'
                    }]
                }
            }
        },
        express:{
            all:{
                options:{
                    port:3000,
                    hostname:'localhost',
                    bases:['./', './demo/'],
                    livereload: false // Disabled because it makes initial load really slow
                },
            }
        }

    });

    // Tasks
    grunt.registerTask('build', ['clean', 'less_imports', 'string-replace', 'copy', 'less']);
    grunt.registerTask('demo', ['build', 'express', 'open', 'watch']);
    grunt.registerTask('default', ['build']);


};
