'use strict';

angular
  .module("twigkitLightApp")
  .factory('NotificationService', NotificationService);

  NotificationService.$inject = ['$timeout', '$document'];

function NotificationService($timeout, $document) {
  
    var factory = {
      notify: notify,
      error: error,
      warning: warning,
      success: success
    };
  
    return factory;
  
    ///////////////
  
    function error(message) {
      notify(message, 'tk-stl-alertbox-negative');
    }
  
    function warning(message) {
      notify(message, 'tk-stl-alertbox-warning');
    }
  
    function success(message) {
      notify(message, 'tk-stl-alertbox-positive');
    }
  
  
    /**
     * @ngdoc
     * @name lightning.NotificationService#notify
     * @methodOf lightning.NotificationService
     *
     * @description
     * Sends a simple notification to the browser
     * @param {string} text message to display
     */
    function notify(message, type) {
      type = type || '';
      var notfications = angular.element($document[0].getElementsByClassName('tk-stl-notifications'));
      var notify = '<div class="tk-stl-basic-card tk-stl-alertbox fade-in-up ' + type + '">' + message + '</div>';
      notfications.append(notify);
  
      var notification = angular.element(notfications.children()[notfications.children().length - 1]);
  
      // hide later
      $timeout(function () {
        notification.removeClass('fade-in-up').addClass('fade-out-down');
        $timeout(function () {
          notification.remove();
        }, 300);
      }, 3000);
    }
  }