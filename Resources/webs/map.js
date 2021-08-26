var OpenStreetMap_Mapnik = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
});

var googleStreets = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{
    subdomains:['mt0','mt1','mt2','mt3']
});

var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
	subdomains:['mt0','mt1','mt2','mt3']
});

var googleHybrid = L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    subdomains:['mt0','mt1','mt2','mt3']
});

var map = L.map('map', {
	center: [0,0],
	zoom: 2,
	layers: [OpenStreetMap_Mapnik, googleSat, googleHybrid]
	}).fitWorld();

var baseMaps = {
	"OSM": OpenStreetMap_Mapnik,
	"Satilite": googleSat,
	"Hybrid": googleHybrid
};

L.control.layers(baseMaps).addTo(map);
L.control.scale().addTo(map);

var marker;
var MyApp;
new QWebChannel(qt.webChannelTransport, function (channel) 
{
    MyApp = channel.objects.MyApp;
});

/*map.on('click', function(e){
	if (marker == null) {marker = new L.marker(e.latlng).addTo(map);}
	else {marker.setLatLng([e.latlng.lat, e.latlng.lng]).update();}
	map.panTo(e.latlng);
	MyApp.onMapMove(e.latlng.lat, e.latlng.lng)
});*/

map.on('mousemove', function(e)
{
	MyApp.onMapMove(e.latlng.lat, e.latlng.lng)
});

var DrawShapes;
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
  draw: {
    position: 'topleft',
    polygon: {
      allowIntersection: false,
      drawError: {
        color: '#b00b00',
        timeout: 1000
      },
      showArea: true
    },
    /*circle: {
      shapeOptions: {
        color: '#662d91'
      }
    },*/
	circle:false,
    polyline: true,
    rectangle: true,
    marker: true,
  },
  edit: {
    featureGroup: drawnItems
  }
});
map.addControl(drawControl);

map.on('draw:created', function(e) {
  var type = e.layerType,
  layer = e.layer;
  drawnItems.addLayer(e.layer);
});


// begin Kml Loader ------------------------------------------------------------------------------
var kmlcontrol = L.Control.fileLayerLoad({
	// Allows you to use a customized version of L.geoJson.
	// For example if you are using the Proj4Leaflet leaflet plugin,
	// you can pass L.Proj.geoJson and load the files into the
	// L.Proj.GeoJson instead of the L.geoJson.
	//layer: L.geoJson,
	
	// See http://leafletjs.com/reference.html#geojson-options
	//layerOptions: {style: {color:'red'}},
	
	// Add to map after loading (default: true) ?
	//addToMap: true,
	addToMap: false,
	
	// File size limit in kb (default: 1024) ?
	//fileSizeLimit: 1024,
	
	// Restrict accepted file formats (default: .geojson, .json, .kml, and .gpx) ?
	formats: [
		'.geojson',
		'.json',
		'.kml',
		'.kmz',
		'.gpx'
	]
}).addTo(map);

kmlcontrol.loader.on('data:loaded', function (e) {
	// event.layer gives you access to the layers you just uploaded!

	// Add to map layer switcher
	//layerswitcher.addOverlay(event.layer, event.filename);


	// Get the geojson layer which gets added from the file layers
	gLayer = e.layer.getLayers()[0];

	// If it's a KML it will have altitude, so iterate through and strip them out
	newLatLngs = []
	oldLatLngs = gLayer.getLatLngs();
	$(oldLatLngs).each(function(index, obj) {
		newLatLng = {lat: obj.lat, lng: obj.lng} // Can also: new L.LatLng(obj.lat, obj.lng);
		newLatLngs.push(newLatLng);
	})

	// Set the new latlngs for the polygon
	gLayer.setLatLngs(newLatLngs);

	// If someone has drawn something previously we need to wipe it
	drawnItems.eachLayer(function(l) {
		map.removeLayer(l);
	})
	drawnItems.clearLayers();

	// Add the polygon to the map, not sure why this is required but django-leaflet does this
	map.addLayer(gLayer)

	// Add the polygon to the drawnItems featureGroup
	drawnItems.addLayer(gLayer);

	// Django-leaflet does this so just copy it, it seems to make the fileLayer geojson 
	// get saved to the form
	store.save(drawnItems);
});

// end Kml Loader ------------------------------------------------------------------------------


	
	