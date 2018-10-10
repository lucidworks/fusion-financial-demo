'use strict';

/**
 * @ngdoc function
 * @name twigkitLightApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the twigkitLightApp
 */
angular.module('twigkitLightApp')

    .controller('MainCtrl', ['$rootScope', '$scope', '$stateParams', 'ResponseService', '$location', 'ModalService', '$twigkit', '$timeout', '$window', '$state', '$templateCache',
        function ($rootScope, $scope, $stateParams, ResponseService, $location, ModalService, $twigkit, $timeout, $window, $state, $templateCache) {
            $scope.params = $stateParams;
            $scope.urlparams = $location.search();
            $rootScope.redirectTo = function (page) {
                $location.path(page);
            };

            var fileSavedListener = $rootScope.$on('file_saved', function () {
                $templateCache.remove($state.current.templateUrl($stateParams));
                $timeout(function () {
                    $state.reload();
                }, 500);
            });

            $scope.$on('$destroy', function () {
                fileSavedListener();
            });
        }])
        .controller('CodeEditorCtrl',['$rootScope',function($rootScope){
            $rootScope.disableEditor = true;
        }]);

angular.module('twigkitLightApp')
    .filter('encodeURIComponent', function () {
        return window.encodeURIComponent;
    })

    .filter('landingPageLabel', function () {
        return function (input) {
            return input.split('|')[0];
        }
    })

    .filter('landingPageLink', function () {
        return function (input) {
            return input.split('|')[1];
        }
    });