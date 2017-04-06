'use strict';

angular.module('twigkitLightApp').config(function($stateProvider, $urlRouterProvider,$locationProvider) {

  // For any unmatched url, redirect to homepage /
  var defaultPage = '404';
  var landingPage = 'home';
  $locationProvider.html5Mode(false);

    $urlRouterProvider.otherwise(function($injector, $location) {
      console.log($location.path());
        if ($location.path() == '') {
            $location.url(landingPage);
        } else {
            $location.url('/404');
        }
  });

  // Default views
  $stateProvider

        .state('home', {
          url: '^/',
          templateUrl: 'views/home.html',
          controller: 'MainCtrl'
        })

        .state('search', {
                  url: '^/',
                  templateUrl: 'views/search.html',
                  controller: 'MainCtrl'
                })

        .state('productdetail', {
                   url: '^/',
                   templateUrl: 'views/productdetail.html',
                  controller: 'MainCtrl'
                 })

        .state('404', {
            url: '/404',
            templateUrl: 'views/404.html',
            controller: '404Ctrl'
        })

    // Default rule to display view based on url
    .state('page', {
      url: '/{slug}',
      templateUrl: function (params) {

        if (params.slug === '') {
          params.slug = defaultPage;
        }

        return 'views/' + params.slug + '.html';
      },
      controller: 'MainCtrl'
    })

    .state('details', {
      url: '/{slug}/{id}',
      templateUrl: function (params) {

        if (params.slug === '') {
          params.slug = defaultPage;
        }

        return 'views/' + params.slug + '-detail.html';
      },
      controller: 'MainCtrl'
    });
});
