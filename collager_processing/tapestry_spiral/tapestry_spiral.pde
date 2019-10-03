
void makeRound(
  PImage img, 
  float startX, 
  float startY, 
  int numSteps, 
  float offsetX,
  float offsetSteps
) {
  float stepSize = TWO_PI/numSteps;
  for (int i = 0; i < numSteps; i++) {
    pushMatrix();
    translate(startX, startY);
    rotate((offsetSteps * stepSize) + (i*stepSize));
    translate(0, offsetX/2);

    image(img, 0, 0);
    popMatrix();
  }
}


void setup() {
  String path = "/Users/blackmad/Dropbox/Collage/All Playboy Centerfolds, 1953 - 2014/objects/person/";
  File[] files = listFiles(path);
  
  size(1000, 800);
  
  float middleX = width / 2;
  float middleY = height / 2;
  
  PImage oneImage = loadImage(files[0].getPath());
  //makeRound(oneImage, 250, 250);
  
  float chanceInclusion = 0.7;
  float maxSizePercent = 0.25;
  float minSizePercent = 0.03;
  
  float minSizeX = minSizePercent * width;
  float minSizeY = minSizePercent * height;
  float maxSizeX = maxSizePercent * width;
  float maxSizeY = maxSizePercent * height;
  
  int offsetX = 500;
  int offsetStep = 0;
  
  for (File file : files) {
    PImage img = loadImage(file.getPath());  // Load the image into the program
    if (random(1) > chanceInclusion) {
      continue;
    }
    if (!file.getPath().contains("person")) {
      continue;
    }
    
    if (img.width < minSizeX || img.height < minSizeY) {
      println("image too small " + img.width + " " + img.height + " " + file.getPath());
      continue;
    }
    
    if (img.width > maxSizeX || img.height > maxSizeY) {
        float scale = min(maxSizeX/img.width, maxSizeY/img.height);
        img.resize(floor(scale*img.width), floor(scale*img.height));
    } 
    
    float minScale = max(minSizeX/img.width, minSizeY/img.height);
    float scalingFactor = random(minScale, 1.0);
    img.resize(floor(img.width * scalingFactor), floor(img.height *scalingFactor));
 
   fill(0, 255, 0);
   circle(middleX, middleY, 25);
 
    makeRound(img, middleX, middleY, 10, offsetX, offsetStep);
    offsetX -= 50;
    offsetStep += 0.25;
    
    if (offsetX <= 0) {
      break;
    }
  }
}


void draw() {

}
