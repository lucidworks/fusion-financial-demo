describe("functions for constructing JsDoc documentation for suppressing editor warnings", function() {
	it("should construct jsdoc", function() {

		var funcs = new JsDoc();

        var namespace = {
            elements: ["animals:domestic", "cat", "dog"],
            attributes: ["sound", "leash"]
        };
        Telemark.init(namespace, funcs);

        expect(funcs.create_jsdoc().indexOf("/**@namespace animals*/") > 0).toBe(true);
        expect(funcs.create_jsdoc().indexOf("/**@name domestic*/") > 0).toBe(true);
        expect(funcs.create_jsdoc().indexOf("/**@name cat*/") > 0).toBe(true);
        expect(funcs.create_jsdoc().indexOf("/**@name leash*/") > 0).toBe(true);
	});
});