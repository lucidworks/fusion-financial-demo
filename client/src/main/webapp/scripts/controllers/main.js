'use strict';

/**
 * @ngdoc function
 * @name twigkitAsyncApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the twigkitLightApp
 */
angular.module('twigkitLightApp')

  .controller('MainCtrl', ['$scope', '$stateParams', '$twigkit', '$http', '$lightningUrl', '$rootScope', '$state', '$location', '$timeout', '$twigkit', function ($scope, $stateParams, $twigkit, $http, $lightningUrl, $rootScope, $state, $location, $timeout, $twigkit) {
    $scope.params = $stateParams;


    // FUSION INSTANCE PARAMS
    $rootScope.fusionHost = 'http://' + 'localhost';
    $rootScope.fusionPort = '8764';

    // GET USER NAME FROM TWIGKIT

    var contextPath = $twigkit.getContextPath('/');
    $http.get(contextPath + 'twigkit/api/user')
          .success(function (response) {
              userNameMapping(response);
    });

    $scope.$on('resetTour', function () {
        $scope.$broadcast('tutorial_delete');
        $state.reload();
    });

    // WATCH FOR SEARCH
    $scope.$watch(function(){ return $location.search() }, function() {
        getFusionRules();
    });


    // GET AND PARSE RAW FUSION RESPONSE
    // HANDLES BANNERS AND REDIRECTS
    function getFusionRules() {
        console.log("**CHECK FOR RULES**");
        var urlParams = $lightningUrl.getAllUrlParameters();

        if (urlParams.q) {
              var query = '?&wt=json&q=' + encodeURI(urlParams.q).replace(/&/g,'%26').replace(/\//g,'%2F').replace(/#/g,'%23');
            } else {
              var query = '?&wt=json&q=*:*'; //Set q to *:* when q is empty.  Usually when loading UI initially
            };
        query += '&debug=false&fl=score';

        // HARDCODED, FIX
        var fusionAuthHeader = {headers: {'Authorization': 'Basic ' + btoa('admin' + ':' + 'password123')}};
        var url = $rootScope.fusionHost + ':' + $rootScope.fusionPort + '/api/apollo/query-pipelines/twigkit-rules-compatibility/collections/ecommerce/select' + query;

        $http.get(url,fusionAuthHeader).success(function(data, http_code, headers, config) {
              //With success, add INFO message to console and pass http response to search page fields
              console.log('**RULES SUCCESS** code=' + http_code,'data=', data);
              processBanner(data);
              $timeout(function() {
                processRedirect(data);
              });
            }).error(function(data, http_code, headers, config) {
              console.log('**RULES ERROR** code=' + http_code + ', data=');
              console.log(data);
        });
    }

    // HELPER FUNCTIONS
    function processBanner(data) {
        if (data.fusion.banner) {
            $scope.isBanner = true;
            $scope.bannerData = data.fusion.banner[0];
        }
        else {
            $scope.isBanner = false;
        }
    }

    function processRedirect(data) {
        if (data.fusion.redirect) {
            $scope.$apply(function() { $location.path(data.fusion.redirect); });
        }
    }

    function userNameMapping(username) {
        console.log(username);
        $rootScope.user = capitalizeFirstLetter(username.id);
        if (username.id.toLowerCase() == 'admin') {
           $rootScope.userid = 'f42b7e68313e4cf26b62b83d97bf2a3d79d80ac9';
           $lightningUrl.setUrlParameter('c', 'userId['+$rootScope.userid+']', true);
        }
        else if (username.id.toLowerCase() == 'andy') {
           $rootScope.userid = 'f000240dd0c1577a36daac3082af3f886e8641d6';
           $lightningUrl.setUrlParameter('c', 'userId['+$rootScope.userid+']', true);
        }
        else if (username.id.toLowerCase() == 'josh') {
           $rootScope.userid = 'f000240dd0c1577a36daac3082af3f886e8641d6';
           $lightningUrl.setUrlParameter('c', 'userId['+$rootScope.userid+']', true);
        }
    }

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
  }]);
