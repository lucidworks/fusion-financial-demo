'use strict';

/**
 * @ngdoc function
 * @name twigkitLightApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the twigkitLightApp
 */
angular.module('appkitApp')

    .controller('MainCtrl', ['$rootScope', '$scope', '$stateParams', 'ResponseService', '$location', 'ModalService', '$twigkit', '$timeout', '$sce', '$state', '$http', function ($rootScope, $scope, $stateParams, ResponseService, $location, ModalService, $twigkit, $timeout, $sce, $state, $http) {
        $scope.params = $stateParams;
        $scope.urlparams = $location.search();
        $http.get("twigkit/api/app-config/")
            .then(function successCallback(response){
                $rootScope.mapUrl = function(result) {
                    var google_api_key = response.data.googleMapsKey;
                    var query = window.encodeURIComponent(result.fields.city_s.val) + ',' + window.encodeURIComponent(result.fields.state_s.val);
                    return "http://maps.googleapis.com/maps/api/staticmap?zoom=10&size=150x150&maptype=roadmap&markers=color:red%7Clabel:''%7C" + query + "&sensor=false&key="+google_api_key;
                };
            }, function errorCallback(response){
                console.error('failed to get user details: ' + JSON.stringify(response, undefined, 2));
            });

        $scope.filterQueryUrl = function(result, fieldname, page, filter){
            var filterBuffer = "";
            angular.forEach(result.fields[fieldname].val, function(value){
                filterBuffer+="&f="+filter+"['"+value+"']*";
            });
            return "#/"+page+"?"+filterBuffer;
        };


        $twigkit.getUser()
            .then(function (user) {
                $scope.user = user;
                $rootScope.user = user;
                $http.get("twigkit/api/user-profile/" + user.name + "/")
                            .then(function successCallback(response){
                                user.role = response.data.role;
                            }, function errorCallback(response){
                                console.error('failed to get user details: ' + JSON.stringify(response, undefined, 2));
                            });
                });

        $rootScope.redirectTo = function (page) {
            $location.path(page);
        };

        $scope.closeModal = function (name) {
            ModalService.close(name);
        };

        $scope.collaborationTopics = [];

        function getTopics() {
            $twigkit.getTopics()
                .then(
                    function (success) {
                        $scope.collaborationTopics = success.data;
                        angular.forEach($scope.collaborationTopics, function (topic, key) {
                            var options = {
                                topic: topic.id
                            };
                            $twigkit.getBookmarks(null, options)
                                .then(
                                    function (success) {
                                        topic['bookmarks'] = success.data;
                                    },
                                    function (error) {
                                        $log.error(error);
                                    }
                                );
                        });
                    },
                    function (error) {
                        $log.error(error);
                    }
                );
        }

        getTopics();

        $scope.bookmarks = [];
        $scope.portfolioCompanies = {};

        function getBookmarks() {
            var options = {};
            $twigkit.getBookmarks(null, options)
                .then(
                    function (success) {
                        $scope.bookmarks = success.data;
                        angular.forEach(success.data, function(bookmark){
                            if(typeof $scope.portfolioCompanies[bookmark.target] == 'undefined'){
                                $scope.portfolioCompanies[bookmark.target] = [];
                                $scope.portfolioCompanies[bookmark.target].push(bookmark.topic);
                            }else{
                                $scope.portfolioCompanies[bookmark.target].push(bookmark.topic);
                            }
                        });
                    },
                    function (error) {
                        $log.error(error);
                    }
                );
        }

        getBookmarks();


        $scope.deleteCollaboration = function (id) {
            $twigkit.deleteTopic(id).then(function () {
                $rootScope.$broadcast('topic_removed');
                $scope.closeModal('deleteCollaborationModal');
                getTopics();
            }, function (data) {
                console.log('Error');
                console.log(data);
            });
        };

        $scope.deleteBookmark = function (id) {
            $twigkit.deleteBookmark(id).then(function () {
                $rootScope.$broadcast('bookmark_removed');
                $scope.closeModal('deleteBookmarkModal');
                getTopics();
            }, function (data) {
                console.log('Error');
                console.log(data);
            });
        };


    }]);


angular.module('appkitApp')
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