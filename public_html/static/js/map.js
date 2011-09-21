var dataURL = "static/data/meetups.json";

var po = org.polymaps;
var map;

var categories = [];
var selectedCategory = "All";

var layers = [];
var layerProperties = [];

function createMap() {

	map = po.map()
	    .container(document.getElementById("map").appendChild(po.svg("svg")))
	    .center({lat: 37.7833333, lon: -122.410667})
		.zoom(16)
	    .zoomRange([10, 18])
	    .add(po.interact());

	map.add(po.image()
	    .url(po.url("http://{S}tile.cloudmade.com"
	    + "/af6cad3a3c93413aaa8c2edd19a6d688" // gray dawn with the weeplaces api key
	    + "/22677/256/{Z}/{X}/{Y}.png")
	    .hosts(["a.", "b.", "c.", ""])));
	
	$.ajax({
	 	url: "http://tendermaps.com/layers.json",
		contentType: 'text/javascript',
  
        // on complete. will have to get used to all these inline functions
        success: function(data){
      
	        // parse the shit out of this
	        var l = JSON.parse(data);
			
			for (var i = 0; i < l.length; i++) {
				var layer = l[i];
				layerProperties[i] = layer;
				loadLayer(layer.url);
			}
		}
	});
}

function loadLayer(layerURL) {
	
	var img;
	map.add(img = po.image()
	    .url(po.url(layerURL + "{Z}/{X}/{Y}.png")));
	
	// transparency for image layers
	img.container().style.opacity = 1;

	layers.push(img);
	
	map.add(po.compass()
	    .pan("none"));
}
