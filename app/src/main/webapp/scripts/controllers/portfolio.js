'use strict';

/**
 * @ngdoc function
 * @name twigkitLightApp.controller:PortfolioCtrl
 * @description
 * # MainCtrl
 * Controller of the twigkitLightApp
 */
angular.module('twigkitLightApp')

  .controller('PortfolioCtrl', ['$rootScope', '$scope', '$stateParams', 'ResponseService', '$location', 'ModalService', '$twigkit', '$state', '$lightningUrl', function ($rootScope, $scope, $stateParams, ResponseService, $location, ModalService, $twigkit, $state, $lightningUrl ) {
    $scope.params = $stateParams;
    $scope.urlparams = $location.search();
    $twigkit.getUser()
        .then(function (user) {
        $scope.user = user;
    });
    $rootScope.redirectTo = function(page){
      $location.path(page);
    };

      $scope.closeModal = function (name) {
          ModalService.close(name);
      };

    $scope.collaborationTopics = {};

    function getTopics() {
      $twigkit.getTopics()
        .then(
          function (success) {
              angular.forEach(success.data,function(topic){
                  $scope.collaborationTopics[topic.id] = topic;
                  $scope.collaborationTopics[topic.id]["companies"] = [];
                  var options = {
                      topic: topic.id
                  };
                  $twigkit.getBookmarks(null, options)
                      .then(
                          function (success) {
                              angular.forEach(success.data,function(bookmark){
                                  $scope.collaborationTopics[topic.id]["companies"].push(bookmark.target);
                              });
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

    function getBookmarks (topicid) {
        var options = {
            topic: topicid
        };
        $twigkit.getBookmarks(null, options)
        .then(
          function (success) {
              $scope.bookmarks = success.data;
          },
          function (error) {
              $log.error(error);
          }
        );
    }

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

    $scope.deleteBookmarkByTarget = function (topicid, target) {
        var options = {
            topic: topicid
        };
        $twigkit.getBookmarks(null, options)
            .then(
                function (success) {
                    angular.forEach(success.data,function(bookmark){
                        if(bookmark.target == target){
                            $twigkit.deleteBookmark(bookmark.id).then(function () {
                                getTopics();
                                $lightningUrl.reloadSearch();
                            }, function (data) {
                                console.log('Error');
                                console.log(data);
                            });
                        }
                    });
                },
                function (error) {
                    $log.error(error);
                }
            );
    };

  }]);


angular.module('twigkitLightApp').filter('encodeURIComponent', function() {
  return window.encodeURIComponent;
});

angular.module('twigkitLightApp').filter('contains', function() {
    return function (array, needle) {
        return array.indexOf(needle) >= 0;
    };
});
