// scaling is wrong
// not filling up corners
// for rotations, would be nice to use a truncated version of the image based on initial rotation, so that you get a continuous effect 

void makeCascade(PImage img, int startX, int startY) {
  float minScale = 0.1;
  float maxScale = 2.0;
  int numSteps = 10;
  float overlapPercent = 0.4;
  //int startX = 0;
  //int startY = 0;
  
  boolean getSmaller = random(1) > 0.5;
  boolean centerMovement = random(1) > 0.7;
  int direction = random(1) > 0.5 ? -1 : 1;
  
  int lastHeight = img.height;
  int lastWidth = img.width;
  
  for (int i = 0; i < numSteps; i++) {
    float factor = (i+1)*1.0/ numSteps;
    
    if (getSmaller) {
      factor = 1.0 - factor;
    }
    float scaling = minScale + (factor * (maxScale - minScale));

      
    PImage scaledImage = img.copy();
    int newWidth = floor(img.width * scaling);
    int newHeight = floor(img.height * scaling);
    scaledImage.resize(newWidth, newHeight);
    //println(scaling);
    
    if (centerMovement) {
      startY += direction*(lastHeight - newHeight)*1.0/2;
    }
    
    image(scaledImage, startX, startY);
    
    startX += direction * newWidth * overlapPercent;

    lastHeight = newHeight;
    lastWidth = newWidth;
  }
}

void makeRound(PImage img, int startX, int startY) {
  int numSteps = 10;
  for (int i = 0; i < numSteps; i++) {
    pushMatrix();
    translate(
      width/2-img.width/2+(startX-width/2), 
      height/2-img.height/2+(startY-height/2)
    );
    rotate(i*TWO_PI/numSteps);
    image(img, 0, 0);
    popMatrix();
  }
}


void setup() {
  String path = "/Users/blackmad/jpegs/objects";
  File[] files = listFiles(path);
  
  size(1000, 1000);
  
  PImage oneImage = loadImage(files[0].getPath());
  //makeRound(oneImage, 250, 250);
  
  float chanceInclusion = 0.3;
  float maxSizePercent = 0.25;
  float minSizePercent = 0.03;
  
  float minSizeX = minSizePercent * width;
  float minSizeY = minSizePercent * height;
  float maxSizeX = maxSizePercent * width;
  float maxSizeY = maxSizePercent * height;
  
  for (File file : files) {
    PImage img = loadImage(file.getPath());  // Load the image into the program
    println(file.getPath());
    
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
 
    int imageOverdraw = 150;
    makeCascade(img,
    floor(random(width+imageOverdraw)-imageOverdraw/2), 
    floor(random(height+imageOverdraw)-imageOverdraw/2));
  }
}


void draw() {

}
