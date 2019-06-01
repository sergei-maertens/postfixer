'use strict';
var gulp = require('gulp');
var webpack = require('webpack-stream');
var paths = require('../paths');
var webpackConfig = require('../../webpack.config.js');


/**
 * Js task
 * Run using "gulp js"
 * Runs webpack to compile javascript
 */
function js() {
    return gulp.src(paths.jsEntry)
        .pipe(webpack(webpackConfig))
            .on('error', function () {
              this.emit('end');
            })
        .pipe(gulp.dest(webpackConfig.output.path));
};

gulp.task('js', js)
exports.js = js;
