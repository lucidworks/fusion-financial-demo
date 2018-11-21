__webpack_public_path__ = window.__webpack_public_path__ = document.getElementsByTagName('base')[0].href.replace(/\/$/, '') + '/builder/build/';

'use strict';
import { ComponentsModule } from './components/components.module';
import { RoutesModule } from './routes/routes.module.js';
import { SearchController } from './controllers/search.controller';

let appModule = angular
  .module('appStudioSearch', [
    , 'ui.router'
    , 'ngAnimate'
    , 'lightning'
    , RoutesModule.name
    , ComponentsModule.name
  ])
    .run(['$rootScope', '$http', '$twigkit', function ($rootScope, $http, $twigkit) {
    var contextPath = $twigkit.getContextPath('/');
    var url = contextPath + 'twigkit/api/app/title';
    $http.get(url).then(function (data) {
      $rootScope.application_name = data.data['application-title'];
    });

    $rootScope.$on('response_response_error', function (response) {
      $rootScope.showErrorModal = true;
    });

    $rootScope.closeErrorModal = function () {
      $rootScope.showErrorModal = false;
    }
  }])
  .controller('searchCtrl', SearchController);

angular.bootstrap(document, ['appStudioSearch']);