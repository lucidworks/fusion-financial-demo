'use strict';

/**
 * @ngdoc function
 * @name twigkitLightApp.controller:CompanyCtrl
 * @description
 * # MainCtrl
 * Controller of the twigkitLightApp
 */
angular.module('twigkitLightApp')

  .controller('CompanyCtrl', ['$rootScope', '$scope', '$stateParams', 'ResponseService', '$location', 'ModalService', '$twigkit', '$state', function ($rootScope, $scope, $stateParams, ResponseService, $location, ModalService, $twigkit, $state ) {
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

    $scope.parentTopics = {};

    function getTopicsForCompany () {
      var options = {
          target: $scope.params.id
      };
      $twigkit.getBookmarks(null, options)
          .then(
              function (success) {
                  angular.forEach(success.data, function(bookmark){
                      $scope.parentTopics[bookmark.topic.id.toString()] = bookmark.topic;
                  });
              },
              function (error) {
                  $log.error(error);
              }
          );
    }

    $scope.collaborationTopics = {};

      function getTopics() {
          $twigkit.getTopics()
              .then(
                  function (success) {
                      angular.forEach(success.data,function(topic){
                          if(typeof $scope.parentTopics[topic.id] == 'undefined'){
                              $scope.collaborationTopics[topic.id] = topic;
                          }
                      });
                  },
                  function (error) {
                      $log.error(error);
                  }
              );
      }

    getTopicsForCompany();
    getTopics();

    $scope.bookmarkResult = function(result,topicid){
        var data = {
        target: result.fields.ticker_s.val[0],
        title: result.fields.company_name_s.val[0],
        topic: topicid,
        url: "#/companies/"+result.fields.ticker_s.val[0]
        };
        $twigkit.postBookmark(data)
        .then(
            function(){
                $scope.parentTopics[topicid] = $scope.collaborationTopics[topicid];
                delete $scope.collaborationTopics[topicid];
                getTopicsForCompany();
                getTopics();
            },function(error){
                $log.error(error);
            }
        );
    };


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

      $scope.isEmptyObject = function( obj ) {
          for ( var name in obj ) {
              return false;
          }
          return true;
      }

  }]);


angular.module('twigkitLightApp').filter('encodeURIComponent', function() {
  return window.encodeURIComponent;
});
