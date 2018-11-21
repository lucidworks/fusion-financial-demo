  /*@ngInject*/
export function RoutesConfig($locationProvider, $urlRouterProvider) {
  // $locationProvider.html5Mode({
  //   enabled:true,
  //   requireBase:false
  // });

  const defaultPage = '/search';
  $urlRouterProvider.otherwise(defaultPage);
  $locationProvider.html5Mode(false);
}
