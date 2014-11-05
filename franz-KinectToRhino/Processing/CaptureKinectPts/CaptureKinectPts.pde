import processing.opengl.*;
import SimpleOpenNI.*;  // Download from: https://code.google.com/p/simple-openni/

// filename for the textfile  
String fileName = "test4.txt";  

// determine resolution (1=highest, 2=lower (skip points)...)"
int res = 2;

SimpleOpenNI kinect;

float rotation = 0;

PVector[] depthPoints;
PImage rgbImage;

PVector currentPoint;
color tempColor;

PrintWriter output;


void setup() {
  size(1024, 768, OPENGL);
  kinect = new SimpleOpenNI(this);
  kinect.enableDepth();
  // access the color camera
  kinect.enableRGB(); 
  // tell OpenNI to line-up the color pixels
  // with the depth data
  kinect.alternativeViewPointDepthToImage(); 

  output = createWriter(fileName); 
   
}

void draw() {
  background(0);
  kinect.update();
  // load the color image from the Kinect
  rgbImage = kinect.rgbImage(); 

   
  translate(width/2, height/2, -200);
  rotateX(radians(180));
  
  //rotateY(radians(rotation));
  //rotation++;

  // get vectors from the depthMap
  depthPoints = kinect.depthMapRealWorld();
  
  // browse through all depth points (skips points according to resolution settings)
  for (int i = 0; i < depthPoints.length; i+=res) {
    currentPoint = depthPoints[i];
    // set the stroke color based on the color pixel
    stroke(rgbImage.pixels[i]); 
    point(currentPoint.x, currentPoint.y, currentPoint.z);
  }
}

void exportToTxtfile() {
  
  println("start export..");
  
  for (int i = 0; i < depthPoints.length; i+=res) {
    currentPoint = depthPoints[i];
    tempColor = rgbImage.pixels[i];
    
    if (currentPoint.x+currentPoint.y+currentPoint.z != 0) {
      output.println(currentPoint.x + "," + currentPoint.y + "," + currentPoint.z+"," + red(tempColor) + "," + green(tempColor) + "," + blue(tempColor) );
    }
    
  }
  
  println("export.done!");
  exit();

}


void keyReleased() {
  
  if (keyCode == 82) { // if "r" is released
      exportToTxtfile();
  }
}

