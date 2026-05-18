// Download ESA Land Cover

// var harvey_roi = ee.Geometry.Rectangle([-95.92, 30.20, -94.02, 28.74]);
// Map.addLayer(harvey_roi, {color: 'red'}, 'Harvey Bounding Box', false);


// Define a Point object (longitude, latitude)
var point = ee.Geometry.Point([-95.2741, 29.7021]);

// Apply the buffer method (100 meters)
var roi = point.buffer({'distance': 15000});

// Display result
//Map.addLayer(point, {'color': 'black'}, 'Point');
Map.addLayer(roi, {'color': 'red'}, 'Buffer', false);


// Load ESA Data
var esa = ee.ImageCollection("ESA/WorldCover/v100").first();
var visualization = {bands: ['Map']};

var esa_clip = esa.clip(roi);
Map.addLayer(esa_clip, visualization, 'ESA Land Cover');
Map.centerObject(roi, 6);

// Get the projection (10m)
print('Projection:', esa.projection());
print('Scale in meters:', esa.projection().nominalScale());


// EPSG:4326 (WGS 84): Used in GPS and global mapping; uses longitude/latitude.
// EPSG:3857 (WGS 84 / Pseudo-Mercator): Used by Web Maps (Google Maps, OpenStreetMap).
// EPSG:4269 (NAD83): Commonly used for North American mapping.

// 3. Define the target CRS (e.g., NAD83 EPSG:3240)
// Replace with the appropriate EPSG for your area
var targetCRS = 'EPSG:3240'; 
var targetScale = 90;

// 4. Resample and Reproject
// .resample() sets the method for the next projection
// .reproject() forces the change in resolution and CRS
var resampled = esa_clip
  .resample('bilinear') // or 'bicubic' or 'nearest'
  .reproject({
    crs: targetCRS,
    scale: targetScale
  });


//print('Scale in meters:', resampled.projection().nominalScale());
Map.addLayer(resampled, visualization, 'Resampled ESA Land Cover');

//Export to Drive
Export.image.toDrive({
  image: resampled,
  description: "ESA_LULC_ROI",
  scale: 90,
  region: roi,
  maxPixels: 1e13
});

// Add a legend to the map
var legend = ui.Panel({style: {position: 'bottom-right', padding: '8px 15px'}});
var title = ui.Label({value: 'ESA Land Cover Legend', style: {fontWeight: 'bold', fontSize: '18px'}});
legend.add(title);

var classes = ['Trees', 'Shrubland', 'Grassland', 'Cropland', 'Built-up', 'Bare', 'Snow/Ice', 'Water', 'Wetland', 'Mangroves', 'Moss'];
var colors = ['#006400', '#ffbb22', '#ffff4c', '#f096ff', '#fa0000', '#b4b4b4', '#f0f0f0', '#0064c8', '#0096a0', '#00cf75', '#fae6a0'];

for (var i = 0; i < classes.length; i++) {
  legend.add(ui.Panel([
    ui.Label({style: {backgroundColor: colors[i], padding: '8px', margin: '0 0 4px 0'}}),
    ui.Label({value: classes[i], style: {margin: '0 0 4px 4px'}})
  ], ui.Panel.Layout.flow('horizontal')));
}
Map.add(legend);
