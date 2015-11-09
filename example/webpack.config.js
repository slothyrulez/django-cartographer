// var path = require("path");
// var webpack = require('webpack');
// var BundleTracker = require('webpack-bundle-tracker');
//
//
// module.exports = {
//   context: __dirname,
//   entry: './assets/js/index',
//   output: {
//       path: path.resolve('./assets/bundles/'),
//       filename: "[name]-[hash].js",
//   },
//
//   plugins: [
//     new BundleTracker({filename: './webpack-stats.json'}),
//   ],
//
//   module: {
//     loaders: [
//       // we pass the output from babel loader to react-hot loader
//       { test: /\.jsx?$/, exclude: /node_modules/, loaders: ['babel'], },
//     ],
//   },
//
//   resolve: {
//     modulesDirectories: ['node_modules', 'bower_components'],
//     extensions: ['', '.js', '.jsx']
//   },
// }
var path = require("path");
var webpack = require('webpack');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,

// entry point of our app. assets/js/index.js should require other js modules and dependencies it needs
  entry: [
      'webpack-dev-server/client?http://localhost:3000',
      'webpack/hot/only-dev-server',
      // './assets',
      './assets/js/index',
  ],
  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name]-[hash].js",
      publicPath: 'http://localhost:3000/assets/bundles/',
      // Tell django to use this URL to load packages and not use STATIC_URL + bundle_name
  },

  plugins: [
      new webpack.HotModuleReplacementPlugin(),
      new webpack.NoErrorsPlugin(), // don't reload if there is an error
      new ExtractTextPlugin("[name].css"),
      new BundleTracker({filename: './webpack-stats.json'}),
  ],

  module: {
    loaders: [
      // Extract css files
        {
            test: /\.css$/,
            loader: ExtractTextPlugin.extract("style-loader", "css-loader"),
            include: path.resolve('./assets/css')
        },
        // we pass the output from babel loader to react-hot loader
        { test: /\.jsx?$/, exclude: /node_modules/, loaders: ['react-hot', 'babel'], },
        // to transform JSX into JS
        // { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader'},
    ],
},

  resolve: {
    modulesDirectories: ['node_modules', 'bower_components'],
    extensions: ['', '.js', '.jsx']
  },
}
