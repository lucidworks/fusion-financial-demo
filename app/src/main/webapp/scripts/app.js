'use strict';

/**
 * @ngdoc overview
 * @name twigkitLightApp
 * @description
 * # twigkitLightApp
 *
 * Main module of the application.
 */
angular
  .module('twigkitLightApp', [
  	'ui.router',
    'lightning'
  ]);

angular
  .module("twigkitLightApp")
    .controller("ctrl",
    function($scope){
      $scope.changedValue = function(item) {
        // TODO: if item not null then activate button
        $scope.topic = item.id;
      }
    });

