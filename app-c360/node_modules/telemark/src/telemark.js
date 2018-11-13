/**
 * Telemark
 *
 * @author H. Stefan Olafsson <mr.olafsson@gmail.com> (https://twitter.com/mrolafsson/)
 *
 * @description Library for generating HTML (well any sort of markup) with JavaScript.
 *
 * @param {Object} namespace A list of the elements and attributes for which helper methods should be created.
 * @param exports The object where the methods for generating markup should be registered.
 *
 * @constructor
 *
 */
var Telemark = (function () {
    "use strict";

    var _exports;
    var module = {};

    // TODO Temporary solution to ensure we do not add reserved words
    var reserved = ["break", "case", "catch", "class", "const", "continue", "debugger", "default", "delete", "do", "else", "export", "extends", "finally", "for", "function", "if", "import", "in", "instanceof", "new", "return", "super", "switch", "this", "throw", "try", "typeof", "var", "void", "while", "with", "yield"];

    /**
     * @name build
     * @description Add the helper methods for specific elements and attributes to the context (e.g. window).
     * @private
     *
     * @param {string} name The actual name of the element as it should appear in markup.
     * @param {function} func The element function that uses {@link #el}.
     *
     */
    function _register(name, func) {
        name = _safe_name(name);
        // Supporting namespace prefixes if appropriate
        var pair = name.split(":");
        _exports[pair[0]] = _exports[pair[0]] ? _exports[pair[0]] : {};
        if (pair.length == 2) {
            _exports[pair[0]][pair[1]] = func;
            _exports[pair[0]].el = _exports.el;
            _exports[pair[0]].attr = _exports.attr;
        } else {
            _exports[pair[0]] = func
        }
    }

    /**
     * Creates a JS valid identifier for the element or attribute helper method.
     * @private
     *
     * @param {string} name The name of the element being registered to the namespace.
     * @returns {string} a valid JS identifier.
     */
    function _safe_name(name) {
        // Try and replace non allowed characters
        // TODO This should probably throw some errors?
        name = name.replace(/-/, "_");
        return (((_exports.hasOwnProperty(name) || reserved.indexOf(name) > -1) && !_exports.hasOwnProperty("$" + name)) ? "$" + name : name);
    }
    
    /**
     * Add your own reusable components.
     *
     * @param name name of the component to register.
     * @param func function that returns elements representing the component.
     */
    module.specify = function (name, func) {
        _register(name, func);
    };

    /**
     * Helper methods for generating markup, constructs the namespace specified and attaches to the object provided.
     *
     * @param namespace
     * @param exports
     */
    module.init = function (namespace, exports) {
        // Determining whether to add the markup methods to an existing object (like window) and/or returned.
        var exports = (typeof exports === "undefined") ? {} : exports;

        // Setting the exports object as a member on the module
        _exports = exports;

        /**
         * @name iterate
         * @description Iterate elements in a collection and pass to a callback function that renders elements.
         * @public
         *
         * @param {Object[]} c Collection of items to iterate.
         * @param {iterateCallback} callback Elements or attributes to be added if {@link expr} evaluates to true.
         *
         */
        exports.iterate = function (c, callback) {
            return {
                collection: c,

                /**
                 * A function that handles each member of a collection.
                 *
                 * @callback iterateCallback
                 * @param {Object} Item from collection.
                 */
                _iterate: callback,
                make: function () {
                    if (c != null && typeof c == "object") {
                        var markup = [];

                        if (Array.isArray(c)) {
                          for (var z = 0; z < this.collection.length; z++) {
                            markup.push(
                              this._iterate(
                                this.collection[z]
                              ).make()
                            );
                          }
                        } else {
                            for (var prop in this.collection) {
                                if (this.collection.hasOwnProperty(prop)) {
                                  markup.push(
                                    this._iterate(
                                      this.collection[prop], prop
                                    ).make()
                                  );
                                }
                            }
                        }

                        return markup.join("");
                    } else {
                        return "";
                    }
                }
            }
        };


        /**
         * @name when
         * @description Conditionally add elements or attributes.
         * @public
         *
         * @param {boolean} expr Expression to determine whether to add the nested elements.
         * @param {...*} var_args Elements or attributes to be added if {@link expr} evaluates to true.
         *
         */
        exports.when = function (expr) {
            return {
                _show: expr,
                recipe: expr ? Array.prototype.slice.call(arguments, 1) : [],
                make: function () {
                    if (this._show) {
                        var markup = []
                        build([], markup, this.recipe);
                        return markup.join("");
                    } else {
                        return "";
                    }
                }
            }
        };

        /**
         * Does nothing but return the string for readability of element body.
         *
         * @param text
         * @returns {*}
         */
        exports.text = function (text) {
            return text;
        };

        /**
         * @name attr
         * @description Create an element attribute with a given name and value.
         *
         * @param {string} name
         * @param {Object} value
         */
        exports.attr = function (name, value) {
            return {
                _make_attribute: function () {
                    if (name && value) {
                        return name + "=\"" + value + "\"";
                    } else {
                        return name;
                    }
                }
            };
        };

        /**
         * @name build
         * @description Turns element and attribute objects into a markup array of strings.
         * @function
         * @private
         *
         * @param {stringp[]} attributes
         * @param {string[]} markup
         * @param {Object[]} recipe
         */
        function build(attributes, markup, recipe) {
            for (var n = 0; n < recipe.length; n++) {
                if (recipe[n].hasOwnProperty("_make_attribute")) {
                    attributes.push(recipe[n]._make_attribute());
                } else if (recipe[n].hasOwnProperty("_show") && recipe[n]._show !== false) {
                    build(attributes, markup, recipe[n].recipe);
                } else if (typeof recipe[n] === "string") {
                    markup.push(recipe[n]);
                } else if (recipe[n].hasOwnProperty("make")) {
                    markup.push(recipe[n].make());
                }
            }
        }

        // Create an element with a particular name. Helper methods will then be created based on the namespace/attributes.
        /**
         * @name el
         * @description Create an element with a particular name, attributes and child elements if they're passed as parameters.
         * @public
         *
         * @param {string} name
         * @param {...*} var_args Elements or attributes to be added to the body of this element.
         *
         */
        exports.el = function (name) {
            var attributes = [];
            var markup = [];

            for (var i = 1; i < arguments.length; i++) {
                if (Object.prototype.toString.call(arguments[i]) === "[object Arguments]") {
                    build(attributes, markup, arguments[i]);
                } else {
                    build(attributes, markup, Array.prototype.slice.call(arguments, 1));
                    break;
                }
            }

            return {
                prepend: function (el) {
                    markup.unshift(el.make());
                },
                append: function (el) {
                    markup.push(el.make());
                },
                set: function (attr) {
                    attributes.push(attr._make_attribute());
                },
                make: function () {
                    return "<" + name + (attributes.length > 0 ? " " + attributes.join(" ") : "") + ">" + markup.join("") + "</" + name + ">";
                }
            };
        };

        var elements = (namespace.constructor === Array ? namespace : namespace.elements);
        var attrs = (namespace.constructor === Array ? [] : namespace.attributes);

        // Generating helper methods for all the tag/element names specified by the namespace object.
        for (var e = 0; e < elements.length; e++) {
            _register(elements[e], new Function("return this.el(\"" + elements[e] + "\", arguments);"));
        }

        // Generating helper methods for any attributes if specified.
        for (var a = 0; a < attrs.length; a++) {
            _register(attrs[a], new Function("value", "return this.attr(\"" + attrs[a] + "\", value);"));
        }

        return exports;
    };

    return module;

})();

if (typeof exports !== "undefined") {
    if (typeof module !== "undefined" && module.exports) {
        exports = module.exports = Telemark;
    }
    // But always support CommonJS module 1.1.1 spec (`exports` cannot be a function)
    exports = Telemark;
}