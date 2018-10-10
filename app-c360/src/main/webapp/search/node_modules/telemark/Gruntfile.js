/*global module:false*/
module.exports = function(grunt) {

	// Project configuration.
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		banner: '/*! <%= pkg.title || pkg.name %> - v<%= pkg.version %> - ' +
			'<%= grunt.template.today("yyyy-mm-dd") %>\n' +
			'<%= pkg.homepage ? "* " + pkg.homepage + "\\n" : "" %>' +
			'* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>;' +
			' Licensed <%= _.pluck(pkg.licenses, "type").join(", ") %> */\n',
		uglify: {
			options: {
				banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
			},
			build: {
				files: [{
					expand: true,
					cwd: 'src/',
					src: '**/*.js',
					dest: 'dist/',
					ext: '.min.js',   // Dest filepaths will have this extension.
          		  	extDot: 'first'   // Extensions in filenames begin after the first dot
				}]
			}
		},
        concat: {
            options: {
                separator: ';',
            },
            dist: {
                files: {
                    'dist/telemark-html.min.js': ['dist/telemark.min.js', 'dist/telemark-html-plugin.min.js'],
                    'dist/telemark-angular.min.js': ['dist/telemark.min.js', 'dist/telemark-angular-plugin.min.js'],
                }
            },
        },
		jasmine: {
			pivotal: {
				src: ['src/telemark.js', 'src/telemark-html-plugin.js', 'src/telemark-angular-plugin.js', 'src/telemark-jsdoc-plugin.js'],
				options: {
					specs: 'spec/*-spec.js',
					helpers: 'spec/*-helper.js'
				}
			}
		},
	});

    grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-uglify')
	grunt.loadNpmTasks('grunt-contrib-jasmine');

	// Default task(s).
	grunt.registerTask('default', ['jasmine', 'uglify', 'concat']);

};
