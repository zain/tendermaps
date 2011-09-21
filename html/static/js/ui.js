var topicURL = "static/data/topic_rollup.json";

var selectedEvent;
var savedEvents = [];
var selectedTopics = [];

var allTopics = [];
var minimum = 0;
var savedCount = 0;

function initializeUI() {
	initializeInfoWindow();
	initializeSlider();
	initializeTopicFilter();
	
	hideHoverWindow();
	
	$(this).mousemove(onMouseMove);
}

function initializeSlider() {
	$("#slider").slider({
	  min: 0, max: 100, value: minimum, slide: function(e, ui) {

		minimum = ui.value;
		
		var i = layers.length * (ui.value / 100);

		// test performance
		// var t = (new Date()).getTime();
		
		for (var j = 0; j < layers.length; j++) {
			var layer = layers[j];
			var dif = Math.abs(j - i);
			layer.container().style.opacity = .5 - (Math.min(layers.length, dif) / layers.length) * .5;
		}
		
		var k = Math.floor(i);
		layers[k].container().style.opacity = 1;
		
		$("#individualMapType").html(layerProperties[k].map + ', ' + layerProperties[k].person.join(" "));
		$("#individualMapDesc").html(layerProperties[k].description);

		// log ms to complete
		// console.log(((new Date()).getTime() - t) + 'ms to complete');
	  }
	});
	
	// turn the transport method radiobuttons into tab buttons
	$(".buttonSet").buttonset();
}

function initializeTopicFilter() {
	$("#topicFilter").delegate(".topicOption", "click", function() {
		updateTopicFilterView();
	});
	
	$("#about").click(function() {
		$("#aboutInfo").show("fast");
	});
	
	$("#aboutClose").click(function() {
		$("#aboutInfo").hide("fast");
	});
	
	$("input[name=mapTypeRadio]").change(function(e) { 
		var current = ($("input[name=mapTypeRadio]:checked")[0]);
		// console.log(current);
		
		for (var i = 0; i < layers.length; i++) {
			var layer = layers[i];
			var props = layerProperties[i];
			
			if (current.id == "all" || props.map == current.id) {
				map.add(layer);

				map.add(po.compass()
				    .pan("none"));
				
				if (current.id == "all") {
					layer.container().style.opacity = 1;
				}
			}
			else {
				map.remove(layer);
			}
		}
	});
	
	$("input[name=peopleTypeRadio]").change(function(e) {
		var current = $("input[name=peopleTypeRadio]:checked")[0];
		
		for (var i = 0; i < layers.length; i++) {
			var layer = layers[i];
			var props = layerProperties[i];
			
			if (current.id == "allPeople" || props.person.join(" ").search(current.id) >= 0) {
				map.add(layer);
				map.add(po.compass()
				    .pan("none"));
				
				if (current.id == "allPeople") {
					layer.container().style.opacity = 1;
				}
			}
			else {
				map.remove(layer);
			}
		}
	});
}

function initializeInfoWindow() {
	$("#infoClose").click(closeInfoWindow);
	
	$("#infoTweet").click(tweetThis);
	
	// save the venue
	$("#infoSave").click( function() {
		var html = "<div class='savedItem'><span class='savedName'>" + selectedEvent.properties.name + "</span><span class='unsaveEvent'>X</span></div>";
		$("#saved").show("fast").append(html);
		savedCount++;
	});
	
	$("#saved").delegate(".unsaveEvent", "click", function() {
		savedCount--;
		$(this).parent().hide();
		
		if (savedCount <= 0) {
			savedCount = 0;
			$("#saved").hide("fast");
		}
	});
}

function parseTopics() {
	
	allTopics.reverse();
	allTopics = allTopics.slice(100);
	allTopics.reverse();
	for (var i = 0; i < allTopics.length; i++) {
		addCategory(allTopics[i][0], allTopics[i][1]);
	}
	
}

// add the item to the dropdown if possible
function addCategory(category, count) {
	if (category.length && categories.indexOf(category) < 0) {
		var html = "<li onclick=\"updateCategory('" + category + "'	);\"><span class=\"dropdownOption\">" + category + "</span></li>";
		$("#typeFilter .dropdownOptions").append(html);

		categories.push(category);
		
		var id = "checkBox_" + category;
		var checkbox = "<div class='topicOption'><input class='checkboxButton' type='checkbox' id='" + id + "'></input><label for='" + id + "' class='topicDropdownOption unselectable'>" + category + "</label></div>";
		
		$("#topicList").append(checkbox);
	}
}

// when a dropdown item is clicked
function updateCategory(category) {
	selectedCategory = category;
	
	$("#typeFilter .dropdownSelected").html(category);
}

function updateTopicFilterView() {
	
	selectedTopics = [];
	$('input[@type=checkbox][checked]').each(function(index) {
		var topic = this.id.split('_').pop();
		selectedTopics.push(topic);
	});

	if (selectedTopics.length <= 0) {
		$("#selectedTopic").html('Any Topic');
	}
	else if (selectedTopics.length == 1) {
		$("#selectedTopic").html(selectedTopics[0]);
	}
	else if (selectedTopics.length == 2) {
		$("#selectedTopic").html(selectedTopics[0] + ' and ' + selectedTopics[1]);
	}
	else {
		var i = (selectedTopics.length-1);
		var suffix = i > 1 ? i + ' others' : i + ' other';
		$("#selectedTopic").html(selectedTopics[0] + ' and ' + suffix);
	}
}

function updateInfoWindow(data) {
	
	selectedEvent = data;
	
	$("#info").show("fast");
	
	$("#infoTitle").html(data.properties.name);
	$("#infoTime").html(data.properties.date.toDateString() + ' ' + getTime(data.properties.date.getHours()));
	
	var lines = "<span class='mediumText'>" + data.properties.yes_rsvp_count + " rsvps</span>";
	lines = lines + "<br /><span class='mediumText'>" + data.properties.group_name + "</span>";
	lines = lines + "<br /><a href='" + data.properties.event_url + "' target='" + data.properties.group_name + "'>Link to the Event</a>";
	$("#infoDescription").html(lines);
	
	var url = "http://twitter.com/?status=Headed to " + data.properties.name + " this week, via http://bzzy.be";
	var tweetLink = "<a href='" + url + "'>Share on Twitter</a>"
	$("#infoTweet").html(tweetLink);
}

function closeInfoWindow() {
	$("#info").hide("fast");
}

function updateHoverWindow(str, element) {
	$("#hoverLabel").show().html(str);
}

function hideHoverWindow() {
	$("#hoverLabel").hide();
}

function onMouseMove(e) {
	$("#hoverLabel").css('top',  e.pageY + 10);
	$("#hoverLabel").css('left', e.pageX + 10);
}

function tweetThis() {
	console.log("clicked tweet");
}

function getTime(hr) {
	var suffix = hr > 11 ? ":00 PM" : ":00 AM";
	var displayHour = hr > 12 ? hr - 12 : (hr == 0 ? 12 : hr);
	return displayHour + suffix;
}
