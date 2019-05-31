'use strict';
var fs = require('fs');
var path = require('path');

var argv = require('yargs').argv;
var gulp = require('gulp');
var file = require('gulp-file');
var paths = require('../paths');


/** {string} The views directory. */
var VIEWS_DIR = 'views/';


/**
 * Create view task
 * Run using "gulp create-view --name foo [--js --sass --html-include]"
 * Creates files for a new view
 */
gulp.task('create-view', function(cb) {
    if (!argv.name) {
        console.info('Please provide --name argument!');
        return;
    }

    if (!(argv.js || argv.sass || argv.scss || argv.htmlInclude)) {
        console.info('Please provide at least one of the following arguments:');
        console.info('');
        console.info('--js');
        console.info('--sass or --scss');
        console.info('--html-include');
        return;
    }

    var jsViewsDir = paths.jsSrcDir + VIEWS_DIR;
    var sassViewsDir = paths.sassSrcDir + VIEWS_DIR;
    var jsTargetDir = jsViewsDir + argv.name + '/'
    var sassTargetDir = sassViewsDir + argv.name + '/';
    var sassAllContents = '';
    var jsIndexContents = '';

    // Generate JS view if --js is passed
    if (argv.js) {
        new file('index.js', 'import \'./' + argv.name + '\';')
            .pipe(gulp.dest(jsTargetDir));

        new file(argv.name + '.js', '')
            .pipe(gulp.dest(jsTargetDir));

        // Update views/index.js
        setTimeout(function() {
            jsIndexContents = getFolders(jsViewsDir).reduce(function(acc, value) {
                return acc + 'import \'./' + value + '\';\n';
            }, '// THIS IS A GULP GENERATED FILE!!!\n');

            new file('index.js', jsIndexContents)
                .pipe(gulp.dest(jsViewsDir));
        }, 0);
    }

    // Generate SASS view if --sass or --scss is passed
    if (argv.sass || argv.scss) {
        new file('_all.scss', '@import \'' + argv.name + '\'')
            .pipe(gulp.dest(sassTargetDir));

        new file('_' + argv.name + '.scss', '.' + argv.name + ' {\n}')
            .pipe(gulp.dest(sassTargetDir));

        // Update views/_all.scss
        setTimeout(function() {
            sassAllContents = getFolders(sassViewsDir).reduce(function(acc, value) {
                return acc + '@import \'' + value + '/all\';\n';
            }, '// THIS IS A GULP GENERATED FILE!!!\n');

            new file('_all.scss', sassAllContents)
                .pipe(gulp.dest(sassViewsDir));
        }, 0);
    }

    // Creates an HTML file in includes if --html-include is passed
    if (argv.htmlInclude) {
        new file(argv.name + '.html', '')
            .pipe(gulp.dest(paths.htmlTemplatesDir + '/' + argv.name))
    }

    cb();
});


/**
 * Returns all the directories in dir
 * @param {string} dir Path to scan
 * @returns {string[]}
 */
function getFolders(dir) {
    return fs.readdirSync(dir)
        .filter(function(file) {
            return fs.statSync(path.join(dir, file)).isDirectory();
        });
}
