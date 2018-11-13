describe("functions for constructing Angular elements and attributes", function() {
	it("should support basic elements and all angular attributes", function() {
		Angular.init(window);
		expect(html( ng_app("boom") ).make()).toBe("<html ng-app=\"boom\"></html>");
		expect(html( ng_controller("MyController") ).make()).toBe("<html ng-controller=\"MyController\"></html>");
		expect(ng_transclude().make()).toBe("<ng-transclude></ng-transclude>");
	});
});