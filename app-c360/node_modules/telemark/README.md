[![Build Status](https://travis-ci.org/mrolafsson/telemark.svg?branch=master)](https://travis-ci.org/mrolafsson/telemark)
[![Try Telemark on RunKit](https://badge.runkitcdn.com/telemark.svg)](https://npm.runkit.com/telemark)

# Telemark

##### Super-lightweight templating and generation of HTML (and other markup) with plain JavaScript. Works in the browser and Node.js.


## Getting started

Download or install with: `npm install telemark`.

To keep things as compact as possible you can use the library with or without the built-in support for HTML.

```html
<script src="/telemark.min.js"></script><!-- Wow only 2K -->
<script src="/telemark-html-plugin.min.js"></script><!-- Optional -->
```

or get both in one call:

```html
<script src="/telemark-html.min.js"></script><!-- Gosh only 4K -->
```

Getting started is super simple, let's say you want to create HTML you start with the `Telemark.Html()` one:

```javascript
Html.init(window);

ol( $class('beautiful'),
	li('Foo'),
	li('Bar')
).make();
```

This initialiser will add all the helper methods like `ol()`, and `li()` in this case to the global namespace and when you call `make()` generate the following HTML:

```html
<ol class="beautiful">
	<li>Foo</li>
	<li>Bar</li>
</ol>
```

Note, you can also use `require()` where the equivalent would be:

```javascript
var markup = require("telemark/dist/telemark-html.min.js");
markup.html.init(window);
```

> Check out this [code example](https://runkit.com/mrolafsson/telemark-with-express-js) generating [HTML](https://telemark-with-express-js-0f6jnafj3umz.runkit.sh) server-side with [Express.js](http://expressjs.com)!


### Iteration

Did I hear you say loop? Well, golly gosh what a coincidence. This is how you'd generate markup using the built-in `iterate()` method:

```javascript
Html.init(window);

var marx_brothers = ['Groucho', 'Harpo', 'Chico', 'Gummo', 'Zeppo'];

ol( $class('marx'),
	iterate(marx_brothers, function (bro) {
		return li( $class(bro), bro );
	})
).make()
```

In this example you specify the sub-elements you need per entry using an anonymous function. This means that you have full control over the handling of each element in the collection.

You can also do object iteration:

```javascript
var obj = { Perch: 'Embiotocidae', Pike: 'Ptychocheilus grandis', Yellowtail: 'Seriola dorsalis'};
ol(
    iterate(obj, function (value, key) {
        return li( text(key), text(': '), i(value) );
    })
).make()
```

Note that the first argument passed to the function is the value, resulting in the following HTML in this case:

```html
<ol>
    <li>Perch: <i>Embiotocidae</i></li>
    <li>Pike: <i>Ptychocheilus grandis</i></li>
    <li>Yellowtail: <i>Seriola dorsalis</i></li>
</ol>
```

>You can pass into each function any number of elements, and attributes and the library will construct the right markup. Note that if you pass in a simple string it will be used for the body of the element.


### Conditional logic

You can wrap any attributes or elements in a `when( some_expression, ... )`. Only when the first argument evaluates to `true` will the rest of the parameters be executed:

```javascript
ul(
	li( when(false, draggable(false)),
		'Ferris'
	),
	li( when(true, draggable(true)),
		 'Cameron'
	),
	when( false, 
		li('Rooney')
	),
	li( when(false, draggable(false)),
		'Sloane'
	)
)
```

This applies to both attributes and elements as this example shows:

```html
<ul>
	<li>Ferris</li>
	<li draggable="true">Cameron</li>
	<li>Sloane</li>
</ul>
```

In this case, principal Rooney is not added to the list, and only Cameron is draggable.


## Reusable components

You can specify and register your own components that encapsulate logic and return a particular structure:

```javascript
Telemark.specify('telephone', function (name, number) {
    return a( href('tel:' + number), $class('phone-number'), text(name) );
});
```

You can then use these like any other element except that you pass in the parameters you specified:

```javascript
ol(
    li(
        telephone( 'Ghostbusters', '+1-800-555-2368' )
    )
)
```

This would add your component with the specified properties, resulting in this case in the following HTML:

```html
<ol>
    <li>
        <a href="tel:+1-800-555-2368" class="phone-number">Ghostbusters</a>
    </li>
</ol>
```


### Component nesting

If you need components to be able to nest other components you can use the following pattern to define them:

```javascript
Telemark.specify('brothers', function (brothers, nested) {
    return  section(
                ol( $class('brothers'),
                    iterate(brothers, function (brother) {
                        return nested(brother);
                    })
                )
            );
});
Telemark.specify('brother', function (brother) {
    return  li( $class('brother'),
                text(brother)
            );
});
```

You can then use them like this:

```javascript
var marx_brothers = ['Groucho', 'Harpo', 'Chico', 'Gummo', 'Zeppo'];

brothers(marx_brothers, function (name) {
        return brother(name);
}).make()
```


### Building in stages

You don't have to create the markup using one fluent sequence. You can do this in stages and work with the elements at each stage, `append`/`prepend` elements, `set` attributes etc.

```javascript
var brothers = ol( $class('marx') );

var harpo = li('Harpo');
harpo.set( draggable(true) );
brothers.append(harpo);

brothers.prepend( li('Groucho') );
brothers.append( li('Chico') );

brothers.make();
```
		
...will somewhat predictively generate:

```html
<ol class="marx">
	<li>Groucho</li>
	<li draggable="true">Harpo</li>
	<li>Chico</li>
</ol>
```
 
 
## Generating markup using your own element specification

In this case you don't start with `Telemark.Html()` but the core object `Telemark()`. You can pass in your own array of element names which will be turned into helper methods. You can either have these added to the global namespace like this:

```javascript
Telemark.init(['foo', 'bar'], window);

// var markup = require('telemark);
// markup.init(['foo', 'bar'], window);

var my_foo = foo(
	bar('One'), 
	bar('Two')
).make();
```

...will return:

```xml
<foo>
	<bar>One</bar>
	<bar>Two</bar>
</foo>
```

Namespace prefixes are supported but the `:` needs to be replaced with an object dot notation to be a valid identifier:

```javascript
Telemark.init(['movie:science-fiction'], window);

movie.science_fiction().make();
```

...will return:

```xml
<movie:science-fiction></movie:science-fiction>
```

>We try and deal with special characters in element/attribute names e.g. replacing `-` with `_`:

You can use your own holder to keep the global namespace nice and tidy:

```javascript
var _ = Telemark.init(['foo', 'bar']);
_.foo(
    _.bar('One'),
    _.bar('Two')
).make();
```

For HTML plugin you would use the same methodology:

```javascript
var _ = Html.init();
```

If you also want to specify helpers for attributes you can do that:

```javascript
var namespace = {
	elements: ['animals', 'cat', 'dog'],
	attributes: ['sound', 'leash']
};
Telemark.init(namespace, window);

animals(
	dog( sound('woof'), 'Benji' ),
	cat( sound('meow'), leash('no'), 'Garfield' )
)
```

Output:

```xml
<animals>
	<dog sound="woof">Benji</dog>
	<cat sound="meow" leash="no">Garfield</cat>
</animals>
```

You can add any element, regardless of what helper methods you specified using the `el()` function:

```javascript
Telemark.init([], window);

el('foo', 
	el('bar', attr('name', 'thirst'), 
		'First'
	),
	el('bar', 
		'Second'
	),
	el('bar', 
		el('zip',
			'Third'
		)
	)
)
```

...which would conjure up this stirring bit of exemel poetry:

```xml
<foo>
	<bar name="thirst">
		First
	</bar>
	<bar>
		Second
	</bar>
	<bar>
		<zip>Third</zip>
	</bar>
</foo>
```

## Bonus Points: Generating JsDoc to suppress IDE warnings

You can use `Telemark.JsDoc` plugin to generate JsDoc snippets to suppress any warnings the IDE may give you for the helper methods:

```
var funcs = new JsDoc();

var namespace = {
    elements: ['animals:domestic', 'cat', 'dog'],
    attributes: ['sound', 'leash']
};
Telemark.init(namespace, funcs);

console.log(funcs.create_jsdoc());

```

Then copy/paste the snippets into your JS codebase:

```
/**@name iterate*/
/**@name when*/
/**@name attr*/
/**@name el*/
/**@name animals*/
/**@namespace animals*/
/**@name domestic*/
/**@name cat*/
/**@name dog*/
/**@name sound*/
/**@name leash*/
```