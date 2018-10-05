<%@ taglib prefix="wro" uri="/twigkit/wro" %>

<!doctype html>
<html class="no-js">

<head>
    <base href="${pageContext.request.contextPath}/"/>
    <meta charset="utf-8">
    <title>Twigkit</title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width">

    <link rel="stylesheet" type="text/css" href="${pageContext.request.contextPath}/wro/css/main.css" />
    <link rel="icon" href="favicon.ico">
    <link rel="shortcut icon" href="favicon.ico">
</head>

<body ng-app="appkitApp">

<helper:constant name="googleMapApi" value="AIzaSyDjiHy2i5MiQIJmGuhldVedXLuhi6BUris"></helper:constant>

<!-- All views are loaded here -->
<ui-view></ui-view>

<div class="tk-stl-notifications"></div>

<script type="text/javascript" src="${pageContext.request.contextPath}/wro/js/vendor.js"></script>
<script type="text/javascript" src="${pageContext.request.contextPath}/wro/js/main.js"></script>

<script>
    angular.module('lightning').constant('contextPath', '${pageContext.request.contextPath}');
</script>

</body>
</html>
