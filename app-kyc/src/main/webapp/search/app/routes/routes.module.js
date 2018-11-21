import { RoutesConfig } from './routes.config';
import { SearchRoutes } from './search.routes';
import { CoreRoutes } from './core.routes';

export const RoutesModule = angular.module('as.routes', [])
  .config(RoutesConfig)
  .config(CoreRoutes)
  .config(SearchRoutes);

