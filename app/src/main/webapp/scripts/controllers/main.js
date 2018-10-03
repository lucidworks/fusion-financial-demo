'use strict';

/**
 * @ngdoc function
 * @name twigkitLightApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the twigkitLightApp
 */
angular.module('twigkitLightApp')

    .controller('MainCtrl', ['$rootScope', '$scope', '$stateParams', 'ResponseService', '$location', 'ModalService', '$twigkit', '$state', function ($rootScope, $scope, $stateParams, ResponseService, $location, ModalService, $twigkit, $state) {
        $scope.params = $stateParams;
        $scope.urlparams = $location.search();


        $scope.mapUrl = function(result) {
            var query = window.encodeURIComponent(result.fields.City.val) + ',' + window.encodeURIComponent(result.fields.State.val);
            return "http://maps.googleapis.com/maps/api/staticmap?zoom=10&size=150x150&maptype=roadmap&markers=color:red%7Clabel:S%7C" + query + "&sensor=false&key=AIzaSyAHi-dYGeMic0bEjEUq3N2ZG16t8_6mW7s";
        };


        $twigkit.getUser()
            .then(function (user) {
                $scope.user = user;
                $scope.user.name = 'Grant'; // Temporary hack - user names for a demo
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


angular.module('twigkitLightApp').filter('encodeURIComponent', function () {
    return window.encodeURIComponent;
});
