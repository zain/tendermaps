function updateSize() {
	var w = $(window).width();
	var h = $(window).height();

	$('#map').width(w);
	$('#header').width(w - 10);
	$('#map').height(h - 120);
	$('#sidebar').height(h - 320);
	$('#header').height(120);
}