import { get, assign } from 'lodash';

class SearchController {
  /*@ngInject*/
  constructor() {
    assign(this, {});
  }
}

export const SearchComponent = {
  restrict: 'E',
  bindings: {
  },
  controller: SearchController,
  templateUrl: ($stateParams) => {
    const filename = get($stateParams, 'filename', 'search');
    const id = get($stateParams, 'id');
    if (id) {
      return `views/${filename}-detail.html`;
    }
    return `views/${filename}.html`;
  }
};
