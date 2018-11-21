let path = require('path');
let webpack = require('webpack');
let autoprefixer = require('autoprefixer');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
  entry: {
    vendor: path.resolve(__dirname, 'app/vendor.js'),
    app: path.resolve(__dirname, 'app/app.js'),
    // ,lightningCore: 'appkit-ui/dist/js/lightning.core.min.js'
  },
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: '[name].bundle.js',
    // Set dynamically in app.js
    // publicPath: '/search/build/'
  },
  module: {
    rules: [{
      test: /\.js$/,
      use: [{
        loader: 'ng-annotate-loader',
        options: { add: true }
      }, {
        loader: 'babel-loader'
      }
      ],
      include: [
        path.resolve(__dirname, 'app')
      ]
    }, {
      test: /\.html$/,
      use: [
        {
          loader: 'ngtemplate-loader',
          options: { relativeTo: path.resolve(__dirname, '..') + '/' }
        },
        'html-loader'
      ]
    },
    {
      test: /\.css$/,
      use: ['style-loader', 'css-loader']
    },
    {
      test: /\.less$/,
      use: ['style-loader',
        'css-loader',
        {
          loader: 'postcss-loader',
          options: {
            plugins: [
              autoprefixer({ browsers: ['last 2 versions'] })
            ],
            sourceMap: 'inline'
          }
        },
        'less-loader'
      ]
    },
    {
      test: /\.(png|jpg|jpeg|gif|ico|txt)$/,
      loader: 'file-loader?name=[name].[ext]'
    },
    {
      test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: 'url-loader?name=webfonts/[name].[ext]&limit=10000&mimetype=application/font-woff'
    },
    {
      test: /\.(ttf|eot)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: 'file-loader?name=webfonts/[name].[ext]'
    }
    ]
  },
  plugins: [
    new webpack.IgnorePlugin(/\.\/locale$/)
  ],
  target: 'web',
  optimization: {
    minimize: true,
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: false,//true causes slowdown
        sourceMap: true,
        // https://github.com/webpack-contrib/uglifyjs-webpack-plugin#options
        uglifyOptions: {

          mangle: false //true causes slowdown

        }
      })
    ],
    // extra dev config for parity with production mode 
    // see https://medium.com/webpack/webpack-4-mode-and-optimization-5423a6bc597a for more details
    // we can turn on/off as necessary...

    concatenateModules: true,
    flagIncludedChunks: true,
    occurrenceOrder: true,
    sideEffects: true,
    usedExports: true
  }
};
