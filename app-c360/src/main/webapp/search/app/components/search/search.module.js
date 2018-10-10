import { SearchComponent } from './search.component';

import './search.styles.less';

export const SearchModule = angular.module('as.components.search', [])
  .component('search', SearchComponent);