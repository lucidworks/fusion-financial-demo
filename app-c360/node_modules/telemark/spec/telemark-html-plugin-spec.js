describe("functions for constructing HTML", function() {

	Html.init(window);

	it("should construct markup", function() {
		expect(el("whatever").make()).toBe("<whatever></whatever>");
		expect(div().make()).toBe("<div></div>");
		expect(audio().make()).toBe("<audio></audio>");
		expect(href()).toBeDefined();
		
	});
	
	it("should try and not step on it's own toes", function() {
		expect(label).toBeDefined();
		expect($label).toBeDefined();

		expect(label().make()).toBe("<label></label>");
		expect($label("foo")._make_attribute()).toBe("label=\"foo\"");
	});
	
	it("should support nested elements", function() {
		expect(
			ol( attr("class", "beautiful"),
				li("Foo"),
				li("Bar")
			).make()).toBe("<ol class=\"beautiful\"><li>Foo</li><li>Bar</li></ol>");
	});
	
	it("should support conditionals", function() {
		expect(
			ul(
				li( when(false, draggable(false)), "Ferris"),
				li( when(true, draggable(true)), "Cameron"),
				when( false, li("Rooney")),
				li( when(false, draggable(false)), "Sloane")
			).make()).toBe("<ul><li>Ferris</li><li draggable=\"true\">Cameron</li><li>Sloane</li></ul>");
	});
	
	it("should support iteration", function() {
		var marx_brothers = ["Groucho", "Harpo", "Chico", "Gummo", "Zeppo"];
		expect(
			ol( $class("marx"),
				iterate(marx_brothers, function (bro) {
					return li( $class(bro), bro);
				})
			).make()).toBe("<ol class=\"marx\"><li class=\"Groucho\">Groucho</li><li class=\"Harpo\">Harpo</li><li class=\"Chico\">Chico</li><li class=\"Gummo\">Gummo</li><li class=\"Zeppo\">Zeppo</li></ol>");
	});
	
	it("should support building html in stages", function() {
		var brothers = ol( $class("marx") );
	
		var harpo = li("Harpo");
		harpo.set( draggable(true) );
		brothers.append(harpo);
	
		brothers.prepend( li("Groucho") );
		brothers.append( li("Chico") );
		
		expect(brothers.make()).toBe("<ol class=\"marx\"><li>Groucho</li><li draggable=\"true\">Harpo</li><li>Chico</li></ol>");
	});
	
	it("should support html attributes", function() {
		expect(
			a( href("http://foo/"), "Hello" ).make()).toBe("<a href=\"http://foo/\">Hello</a>");
	});

    it("should support defining reusable components", function () {
        Telemark.specify("telephone", function (name, number) {
            return a( href("tel:" + number), $class("phone-number"), text(name) );
        });
        expect(span( telephone( "Ghostbusters", "+1-800-555-2368" ) ).make()).toBe("<span><a href=\"tel:+1-800-555-2368\" class=\"phone-number\">Ghostbusters</a></span>");
    });

    it("should be possible to nest reusable components", function () {
        Telemark.specify("brothers", function (brothers, nested) {
            return  section(
                        ol( $class("brothers"),
                            iterate(brothers, function (brother) {
                                return nested(brother);
                            })
                        )
                    );
        });
        Telemark.specify("brother", function (brother) {
            return  li( $class("brother"),
                        text(brother)
                    );
        });

        var marx_brothers = ["Groucho", "Harpo", "Chico", "Gummo", "Zeppo"];

        expect(
            brothers(marx_brothers, function (name) {
                return brother(name);
            }).make()
        ).toBe("<section><ol class=\"brothers\"><li class=\"brother\">Groucho</li><li class=\"brother\">Harpo</li><li class=\"brother\">Chico</li><li class=\"brother\">Gummo</li><li class=\"brother\">Zeppo</li></ol></section>");
    });
});