<%@ taglib prefix="wro" uri="/twigkit/wro" %>

<!doctype html>
<html class="no-js">

<head>
    <base href="${pageContext.request.contextPath}/"/>
    <meta charset="utf-8">
    <title>Twigkit</title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width">

    <link rel="stylesheet" href="${wro:resourcePath('main.css', pageContext.request)}">
</head>

<body ng-app="twigkitLightApp">

<helper:constant name="googleMapApi" value="AIzaSyCAPCY1ohcDDT-nLGAU6zg7W_-5Rlc5_Ik"></helper:constant>

<!-- All views are loaded here -->
<ui-view></ui-view>

<script src="${wro:resourcePath('vendor.js', pageContext.request)}" type="text/javascript"></script>
<script src="${wro:resourcePath('main.js', pageContext.request)}" type="text/javascript"></script>

</body>
</html>
