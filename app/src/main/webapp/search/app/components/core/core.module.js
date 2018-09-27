import { CoreComponent } from './core.component';

import './core.styles.less';

export const CoreModule = angular.module('as.components.core', [])
  .component('core', CoreComponent);