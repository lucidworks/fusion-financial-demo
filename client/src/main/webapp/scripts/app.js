'use strict';

/**
 * @ngdoc overview
 * @name twigkitLightApp
 * @description
 * # twigkitAsyncApp
 *
 * Main module of the application.
 */
angular
  .module('twigkitLightApp', [
  	'ui.router',
    'ngCookies',
    'ngResource',
    'ngSanitize',
    'ngTouch',
    'lightning',
    'angular-websocket'
  ]);
