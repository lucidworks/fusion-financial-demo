(function(){
    angular.module('docsApp').filter('colonDashCase', function () {
        return function(name){
            var DASH_CASE_REGEXP = /[A-Z]/g;
            var dashed = false;
            return name.replace(DASH_CASE_REGEXP, function (letter, pos) {
                if (!dashed) {
                    dashed = true;
                    return (pos ? ':' : '') + letter.toLowerCase();
                } else {
                    return (pos ? '-' : '') + letter.toLowerCase();
                }
            });
        }
    });
})();