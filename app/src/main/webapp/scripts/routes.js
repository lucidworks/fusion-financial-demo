'use strict';

angular.module('appkitApp').config(function ($stateProvider, $urlRouterProvider, $locationProvider) {

    // For any unmatched url, redirect to homepage /
    var defaultPage = 'home';
    $urlRouterProvider.otherwise(defaultPage);
    $locationProvider.html5Mode(false);

    $stateProvider.state('collaborations', {
        url: '/collaborations',
        templateUrl: 'views/collaborations.html',
        controller: 'CollaborationsCtrl'
    });

    $stateProvider.state('collaboration', {
        url: '/collaborations/{id}',
        templateUrl: function (params) {

            if (params.id === '') {
                return defaultPage;
            }

            return 'views/collaborations-detail.html';
        },
        controller: 'CollaborationDetailCtrl'
    });

    // Default views
    $stateProvider

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


        .state('portfolios-details', {
            url: '/portfolios/{id}',
            templateUrl: function (params) {

                if (params.id === '') {
                    return 'views/' + defaultPage;
                }

                return 'views/portfolios-detail.html';
            },
            controller: 'PortfolioCtrl'
        })

        .state('companies-details', {
            url: '/companies/{id}',
            templateUrl: function (params) {

                if (params.id === '') {
                    return 'views/' + defaultPage;
                }

                return 'views/companies-detail.html';
            },
            controller: 'CompanyCtrl'
        })

        .state('details', {
            url: '/{slug}/{id}',
            templateUrl: function (params) {

                if (params.slug === '' || params.id === '') {
                    params.slug = defaultPage;
                }

                return 'views/' + params.slug + '-detail.html';
            },
            controller: 'MainCtrl'
        })


});
