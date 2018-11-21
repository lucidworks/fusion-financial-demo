import templateUrl from './core.template.html';
import { assign } from 'lodash';

class CoreController {
  /*@ngInject*/
  constructor() {
    assign(this, {});
  }

  $onInit() {
  }
}

export const CoreComponent = {
  restrict: 'E',
  bindings: {},
  controller: CoreController,
  templateUrl: templateUrl
};
