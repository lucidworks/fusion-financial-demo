import { get, includes } from 'lodash';

const templateUrl = ($stateParams) => {
  let filename = get($stateParams, 'filename', 'search');

  if (includes(filename, '.tpl.html')) {
    return `views/partials/${filename}`;
  } else {
    // Strip out .html etc...
    if (includes(filename, '.')) {
      filename = filename.split('.')[0];
    }
    const id = get($stateParams, 'id');
    if (id) {
      return `views/${filename}-detail.html`;
    }
    return `views/${filename}.html`;
  }
}

/*@ngInject*/
export function SearchRoutes($stateProvider) {
  $stateProvider.state('search', {
    // parent: 'core',
    url: '/{filename}',
    params: {
      filePath: null,
      filename: null
    },
    // template: `<search></search>`
    // Have to use controller because lightnings depends on shared scope (It uses $rootScope.$$lastChild)
    controller: 'searchCtrl',
    templateUrl
  });
  $stateProvider.state('detail', {
    // parent: 'core',
    url: '/{filename}/{id}',
    // Have to use controller because lightnings depends on shared scope (It uses $rootScope.$$lastChild)
    controller: 'searchCtrl',
    templateUrl
  });
}
