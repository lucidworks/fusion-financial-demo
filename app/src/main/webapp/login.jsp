<%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
<%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
<%--<%@ taglib prefix="wro" uri="/twigkit/wro" %>--%>
<%@ taglib prefix="app" uri="/lucidworks/app" %>


<!DOCTYPE html>
<%@ page contentType="text/html" pageEncoding="UTF-8" %>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Fusion Search</title>
        <base href="${app:contextPath(pageContext.request)}/" />
        <meta name="description" content="">
        <meta name="author" content="Twigkit">
        <meta name="viewport" content="minimal-ui, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, width=440">

        <link rel="icon" href="${app:contextPath(pageContext.request)}/favicon.ico?v=3" type="image/x-icon"/>

        <%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
        <%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
        <%--<link rel="stylesheet" href="${wro:resourcePath('main.css', pageContext.request)}">--%>

        <%-- Comment this out if you use the WRO4J plugin above --%>
        <%--<link rel="stylesheet" type="text/css" href="${pageContext.request.contextPath}/wro/css/main.css" />--%>
        <%--<link rel="stylesheet" href="${pageContext.request.contextPath}/assets/login.css">--%>

        <link rel="stylesheet" href="${app:contextPath(pageContext.request)}${'/wro/css/main.css'}">
        <link rel="stylesheet" href="${app:contextPath(pageContext.request)}${'/assets/login.css'}">

        <!--[if lt IE 9]>
        <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->
    </head>

    <body class="login app-studio-login" ng-app="twigkitLightApp">

        <div class="login-content" ng-controller="ctrl">
            <helper:title title="{{ $root.application_name }}" ng-if="$root.application_name"></helper:title>
            <widget:login-form
                    method="POST"
                    action="${app:contextPath(pageContext.request)}${'/j_spring_security_check'}"
                    append-hash-to-action="true"
                    branding-class="branding"
                    logo="${app:contextPath(pageContext.request)}${'/assets/logo-icon.png'}"
                    logo-width="136"
                    title="{{$root.application_name}}"
                    title-element="h1"
                    username-class="field required field-email"
                    username-label="Username"
                    password-class="field required field-password"
                    password-label="Password"
                    remember="false"
                    access-denied="login_error"
            ></widget:login-form>

        </div>

        <%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
        <%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
        <%--<script src="${wro:resourcePath('vendor.js', pageContext.request)}" type="text/javascript"></script>--%>
        <%--<script src="${wro:resourcePath('main.js', pageContext.request)}" type="text/javascript"></script>--%>

        <%-- Comment this out if you use the WRO4J plugin above --%>
        <%--<script type="text/javascript" src="${pageContext.request.contextPath}/wro/js/vendor.js"></script>--%>
        <%--<script type="text/javascript" src="${pageContext.request.contextPath}/wro/js/main.js"></script>--%>

        <script src="${app:contextPath(pageContext.request)}${'/wro/js/vendor.js'}" type="text/javascript"></script>
        <script src="${app:contextPath(pageContext.request)}${'/wro/js/main.js'}" type="text/javascript"></script>

        <script>
            angular.module('lightning').constant('contextPath', '${app:contextPath(pageContext.request)}');
        </script>

    </body>
</html>