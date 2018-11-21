/*@ngInject*/
export function CoreRoutes($stateProvider) {
  $stateProvider.state('core', {
    abstract: true,
    template: `<core></core>`
  });
}
