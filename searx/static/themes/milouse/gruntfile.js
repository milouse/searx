module.exports = function(grunt) {

  const path = require('path');

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    watch: {
      scripts: {
        files: ['<%= jshint.files %>', 'less/*.less'],
        tasks: ['jshint', 'concat', 'uglify', 'webfont', 'less:development', 'less:production']
      }
    },
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['js/searx_src/*.js'],
        dest: 'js/searx.js'
      }
    },
    uglify: {
      options: {
        banner: '/*! milouse/searx.min.js | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n',
	output: {
	    comments: 'some'
	},
        ie8: false,
        warnings: true,
        compress: false,
        mangle: true,
        sourceMap: true
      },
      dist: {
        files: {
          'js/searx.min.js': ['<%= concat.dist.dest %>']
        }
      }
    },
    jshint: {
      files: ['js/searx_src/*.js'],
      options: {
        reporterOutput: "",
        proto: true,
        // options here to override JSHint defaults
        globals: {
          browser: true,
          jQuery: false,
          devel: true
        }
      }
    },
    less: {
      development: {
        options: {
          paths: ["less"],
          banner: '/*! searx | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
        },
        files: {
          "css/searx.css": "less/style.less",
          "css/searx-rtl.css": "less/style-rtl.less"
        }
      },
      production: {
        options: {
          paths: ["less"],
          plugins: [
            new (require('less-plugin-clean-css'))({
              advanced: true,
              compatibility: '*'
            })
          ],
          banner: '/*! searx | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
        },
        files: {
          "css/searx.min.css": "less/style.less",
          "css/searx-rtl.min.css": "less/style-rtl.less"
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  grunt.registerTask('test', ['jshint']);

  grunt.registerTask('default', ['jshint', 'concat', 'uglify', 'less:development', 'less:production']);
};
