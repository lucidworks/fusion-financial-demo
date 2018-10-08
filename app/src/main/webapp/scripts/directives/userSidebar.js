/**
 * @ngdoc directive
 * @name lightning.directive:userSidebar
 * @restrict E
 * @author Guy Walker
 *
 * @description
 * Toggle user sidebar
 *
 */

(function () {
    'use strict';

    angular
        .module('lightning')
        .directive('userSidebar', ['$document', userSidebar]);

    function userSidebar($document) {
        var directive = {
            restrict: 'AC',
            link: function (scope, elem) {
                // Bind to user icon to open panel
                var userIcon = angular.element(document.querySelector('#open-user-sidebar'));

                if (userIcon) {
                    userIcon.bind('click', function () {
                        openSidebar();
                    });
                }

                // Bind document click to close on background click
                $document.on('click', function (event) {
                    if (event.srcElement.id != 'open-user-sidebar') {
                        closeSidebar();
                    }
                });

                elem.bind('click', function (event) {
                    event.stopPropagation();
                });

                // Bind close button
                var close = elem.find('close');
                if (close) {
                    close.bind('click', function () {
                        event.stopPropagation();
                        closeSidebar();
                    });
                }

                function openSidebar() {
                    elem.addClass('active');
                }

                function closeSidebar() {
                    elem.removeClass('active');
                }
            }
        };

        return directive;
    }
})();
