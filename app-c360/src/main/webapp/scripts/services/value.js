
'use strict';

angular
  .module('twigkitLightApp')
  .factory('ValueService', ValueService);

  ValueService.$inject = ['$rootScope'];

function ValueService($rootScope) {
  var Values = {};

  var factory = {
    setValue: setValue,
    getValue: getValue
  };

  return factory;

  ///////////////

  function setValue(name, value) {
    Values[name] = value;

    $rootScope.$emit(name + '_value_updated', value);
  }

  function getValue(name, defaultValue) {
    if (Values[name] != undefined) {
      return Values[name];
    }

    return defaultValue;
  }
}

