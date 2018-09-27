<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="app" uri="/lucidworks/app" %>

<!doctype html>
<html class="no-js">

<head>
    <base href="${app:contextPath(pageContext.request)}/" />
    <meta charset="utf-8">
    <title>App Studio IDE</title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width">

    <link rel="icon" href="${app:contextPath(pageContext.request)}/favicon.ico?v=3" type="image/x-icon"/>
    <link rel="stylesheet" type="text/css" href="${app:contextPath(pageContext.request)}/wro/css/main.css" />
</head>

<body>
    <ui-view autoscroll="true" class="routes-container"></ui-view>

    <div class="tk-stl-notifications"></div>

    <div class="tk-stl-modal-wrapper" ng-class="{'show': $root.showErrorModal}">
        <div class="tk-stl-modal tk-rgrid-u-md-1-2 tk-rgrid-u-lg-2-5 tk-rgrid-u-xl-9-24">
            <div class="tk-stl-modal-header">Sorry, but an error occurred while searching <span class="close" ng-click="$root.closeErrorModal()">x</span>
            </div>
            <section class="tk-stl-modal-content">
                <p>Contact your system administrator if this error occurs again</p>
            </section>
        </div>
    </div>

    <script type="text/javascript" src="${app:contextPath(pageContext.request)}/search/build/vendor.bundle.js"></script>
    <script type="text/javascript" src="${app:contextPath(pageContext.request)}/wro/js/lightning.js"></script>
    <script type="text/javascript" src="${app:contextPath(pageContext.request)}/search/build/app.bundle.js"></script>
</body>

</html>