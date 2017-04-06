<!DOCTYPE html>
<%@ page contentType="text/html" pageEncoding="UTF-8" %>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Twigkit</title>
    <meta name="description" content="">
    <meta name="author" content="Twigkit">
    <meta name="viewport" content="minimal-ui; initial-scale=1.0; maximum-scale=1.0; user-scalable=no; width=440">
    <link rel="stylesheet" href="${pageContext.request.contextPath}/assets/login.css">
    <!--[if lt IE 9]>
    <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
</head>

<body class="login">

<div class="login-content">
    <form class="form-login" method="POST" action="${pageContext.request.contextPath}/j_spring_security_check">

        <div class="branding">
            <img src="${pageContext.request.contextPath}/assets/logo.png" width="120" />
            <h1>Please sign in.</h1>
        </div>

        <div class="field required field-email">
            <label for="j_username">Username</label>
            <input id="j_username" name="j_username" type="text" placeholder="Username" />
        </div>
        <div class="field required field-password">
            <label for="j_password">Password</label>
            <input id="j_password" name="j_password" type="password" placeholder="Password" />
        </div>
        <div class="field buttons">
            <button name="submit" type="submit">Sign in</button>
        </div>
        <div class="more">
            <p><a href="/password">Forgotten Password</a> &#149; <a href="/signup">Create Account</a></p>
        </div>
    </form>
</div>

<footer>
    <div class="copyright">&copy; Twigkit 2016</div>
    <nav>
        <ul>
            <li><a href="/help">Help</a></li>
            <li><a href="/terms">Terms</a></li>
        </ul>
    </nav>
</footer>

</body>
</html>