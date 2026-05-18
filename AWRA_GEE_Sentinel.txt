// Download Sentinel 1 Data

var beforeStart = '2017-08-01'
var beforeEnd = '2017-08-23'

var afterStart = '2017-08-25'
var afterEnd =  '2017-09-08'

// var geometry = ee.Geometry.Rectangle([-95.92, 30.20, -94.02, 28.74]);
// Map.addLayer(geometry, {color: 'red'}, 'My Bounding Box', false);

// Define a Point object (longitude, latitude)
var point = ee.Geometry.Point([-95.2741, 29.7021]);

// Apply the buffer method 
var roi = point.buffer({'distance': 25000});

// Display result
Map.addLayer(point, {'color': 'black'}, 'Point');
Map.addLayer(roi, {'color': 'red'}, 'Buffer');


// 3. Speckle Noise Reduction Function
// Sentinel-1 SAR data contains speckle noise, so we smooth it using focal median filter
function reduceSpeckleNoise(image) {
  return image.focalMedian(30, 'square', 'meters')
              .copyProperties(image, image.propertyNames());
}

//Load Sentinel-1 SAR collection and filter 
var afterCollection = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(roi)
  .filterDate(afterStart, afterEnd)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .map(reduceSpeckleNoise)
  .mean();
    
var beforeCollection = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(roi)
  .filterDate(beforeStart, beforeEnd)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .map(reduceSpeckleNoise)
  .mean();

var imageAfter = afterCollection.select(['VV']).clip(roi); 
var imageBefore = beforeCollection.select(['VV']).clip(roi); 

var visParams = {
  min: -20.0,
  max: -4
  
};

Map.addLayer(imageBefore.select(["VV"]), visParams, 'S1 Before Harvey');
Map.addLayer(imageAfter.select(["VV"]), visParams, 'S1 After Harvey');
Map.centerObject(roi, 10);

// Cast all bands to Float32
var imageToExport = imageAfter.toFloat(); 

//Export to Drive
Export.image.toDrive({
  image: imageToExport,
  description: "Sentinel_1_Harvey",
  scale: 30,
  region: roi,
  maxPixels: 1e13
});
