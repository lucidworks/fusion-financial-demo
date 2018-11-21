import { SearchModule } from './search/search.module';
import { CoreModule } from './core/core.module';

export const ComponentsModule = angular.module('as.components', [
  SearchModule.name,
  CoreModule.name
]);
