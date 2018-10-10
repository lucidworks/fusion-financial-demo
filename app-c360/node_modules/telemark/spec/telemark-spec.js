describe("basic functions for constructing markup", function () {

    var module = {};

    it("should work without adding the methods to the global namespace", function () {
        var _ = Telemark.init(["foo", "bar"]);
        expect(window.foo).toBeUndefined();
        expect(_.foo).toBeDefined();
    });

    it("should be able to add markup functions to window object for a nice, neat syntax", function () {
        Telemark.init(["foo", "bar"], window);
        expect(window.foo).toBeDefined();
    });

    it("should try and not step on it's own toes", function () {
        Telemark.init(["el"], window);
        expect(el).toBeDefined();
        expect($el).toBeDefined();

        expect($el().make()).toBe("<el></el>");
    });

    it("should support wrapping text for body of elements with text() to make the code more readable", function () {
        expect(foo( text("bar") ).make()).toBe("<foo>bar</foo>");
    });

    it("should deal with special characters in element names and attributes", function () {
        Telemark.init(["tele-mark"], window);
        expect(tele_mark).toBeDefined();

        expect(tele_mark().make()).toBe("<tele-mark></tele-mark>");
    });

    it("should support namespace prefixes", function () {
        Telemark.init(["movie:science-fiction", "movie:director"], window);
        expect(movie.science_fiction).toBeDefined();
        expect(movie.director).toBeDefined();

        expect(movie.science_fiction().make()).toBe("<movie:science-fiction></movie:science-fiction>");
    });

    it("should work without or without specifying helper methods", function () {
        Telemark.init(["foo"], window);
        expect(
            el("foo",
                el("bar", attr("name", "thirst"), "First"),
                el("bar", "Second"),
                el("bar",
                    el("zip", "Third")
                )
            ).make()).toBe("<foo><bar name=\"thirst\">First</bar><bar>Second</bar><bar><zip>Third</zip></bar></foo>");
    });

    it("should support attributes", function () {
        expect(foo(attr("ding", "dong")).make()).toBe("<foo ding=\"dong\"></foo>");
        expect(foo(attr("ding", "dong"), attr("top", "hat")).make()).toBe("<foo ding=\"dong\" top=\"hat\"></foo>");
    });

    it("should support boolean attributes", function () {
        expect(foo(attr("ding")).make()).toBe("<foo ding></foo>");
    });

    it("should support iteration", function () {
        var list = ["Ding", "Dong"];
        expect(
            foo(
                iterate(list, function (e) {
                    return bar(e);
                })
            ).make()
        ).toBe("<foo><bar>Ding</bar><bar>Dong</bar></foo>")

        expect(
            foo(
                iterate([], function (e) {
                    return bar(e);
                })
            ).make()
        ).toBe("<foo></foo>");

        expect(
            foo(
                iterate(undefined, function (e) {
                    return bar(e);
                })
            ).make()
        ).toBe("<foo></foo>");

        expect(
            foo(
                iterate(null, function (e) {
                    return bar(e);
                })
            ).make()
        ).toBe("<foo></foo>");

        var obj = { Perch: "Embiotocidae", Pike: "Ptychocheilus grandis", Yellowtail: "Seriola dorsalis"};

        expect(
            ol(
                iterate(obj, function (value, key) {
                    return li(text(key), text(": "), i(value));
                })
            ).make()
        ).toBe("<ol><li>Perch: <i>Embiotocidae</i></li><li>Pike: <i>Ptychocheilus grandis</i></li><li>Yellowtail: <i>Seriola dorsalis</i></li></ol>");
    });

    it("should allow you to build markup in stages", function () {
        var namespace = {
            elements: ["animals", "cat", "dog"],
            attributes: ["sound", "leash"]
        };
        Telemark.init(namespace, window);

        var my_animals = animals();

        var benji = dog("Benji");
        benji.set(sound("Woof"));
        benji.set(leash(true));

        my_animals.append(benji);
        my_animals.prepend(cat("Garfield"));

        expect(my_animals.make()).toBe("<animals><cat>Garfield</cat><dog sound=\"Woof\" leash=\"true\">Benji</dog></animals>");
    });

    it("should support nested elements", function () {
        expect(
            foo(
                bar(
                    foo(
                        bar(
                            foo("Foo")
                        )
                    )
                ),
                bar("Bar")
            ).make()).toBe("<foo><bar><foo><bar><foo>Foo</foo></bar></foo></bar><bar>Bar</bar></foo>");
    });

    it("should support basic conditional logic", function () {
        expect(foo(when(true === true, attr("ding"), attr("king", "kong"))).make()).toBe("<foo ding king=\"kong\"></foo>");
        expect(foo(when(0 > 1, attr("ding"), attr("dong")), attr("hah")).make()).toBe("<foo hah></foo>");

        expect(
            foo(
                when(0 > 1, bar("One")),
                bar("Two")
            ).make()).toBe("<foo><bar>Two</bar></foo>");

        expect(
            foo(
                when(true, bar("One")),
                when(true, bar("Two"))
            ).make()).toBe("<foo><bar>One</bar><bar>Two</bar></foo>");

        expect(
            foo(
                when(false, bar("One")),
                when(false, bar("Two"))
            ).make()).toBe("<foo></foo>");

        expect(
            foo(
                bar("One"),
                when(0 > 1, bar("Two")),
                bar("Three")
            ).make()).toBe("<foo><bar>One</bar><bar>Three</bar></foo>");

        expect(
            foo(
                bar("The Dude"),
                when(true === true, bar("Walter")),
                bar("Donny")
            ).make()).toBe("<foo><bar>The Dude</bar><bar>Walter</bar><bar>Donny</bar></foo>");

        expect(
            foo(
                bar(
                    when(true,
                        foo(
                            bar(
                                foo("Foo")
                            )
                        )
                    )
                ),
                bar("Bar")
            ).make()).toBe("<foo><bar><foo><bar><foo>Foo</foo></bar></foo></bar><bar>Bar</bar></foo>");

        expect(
            foo(
                bar(
                    when(false,
                        foo(
                            bar(
                                foo("Foo")
                            )
                        )
                    )
                ),
                bar("Bar")
            ).make()).toBe("<foo><bar></bar><bar>Bar</bar></foo>");
    });

    it("helper functions like iteration and conditional logic should be allowed to be the outermost", function () {
        expect(when(true === true, el("foo")).make()).toBe("<foo></foo>");
        expect(when(true === true, "foo").make()).toBe("foo");
        expect(when(false, el("foo")).make()).toBe("");

        var list = ["Ding", "Dong"];
        expect(iterate(list, function (e) {
                return bar(attr("foo", "bar"), bar(e));
            }).make()
        ).toBe("<bar foo=\"bar\"><bar>Ding</bar></bar><bar foo=\"bar\"><bar>Dong</bar></bar>");

        expect(iterate([], function (e) {
                return bar(e);
            }).make()
        ).toBe("");

        expect(iterate(undefined, function (e) {
                return bar(e);
            }).make()
        ).toBe("");
    });

});
