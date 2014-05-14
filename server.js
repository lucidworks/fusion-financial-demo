var express = require('express');
var app = require('connect');
var serveStatic = require('serve-static');
var request = require('request');
//var errorhandler = require('errorhandler');
var app = express();
var http = require('http');
var path = require('path');

var httpProxy = require('http-proxy');
var proxy = httpProxy.createProxyServer({});

app.set('port', 3334);

//app.use(app.router);


app.use('/solr', function(req, res) {
	var url = "http://localhost:8098/solr" + req.url;
	console.log('Proxying to ' + url);
	req.pipe(request({
		    "url": url,
			"qs": req.query,
			"method": req.method
			}, function(err, errRes){
		    if(err){
			console.log("Proxy =>" + err);
			res.send('Proxy => ' + err);
		    }
		})).pipe(res);
    });
app.use(serveStatic(path.join(__dirname, 'static')));
app.use(require('errorhandler'));

http.createServer(app).listen(app.get('port'), function(){
	console.log('Dev server listening on port ' + app.get('port'));
    });
