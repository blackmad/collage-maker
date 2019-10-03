function setup() {
  //String path = "/Users/blackmad/Code/collage-maker/Mask_RCNN/objects";
  File[] files = listFiles(path);
  size(640, 360);
  img = loadImage(files[0]);  // Load the image into the program
  image(img, 0, 0);
}


function draw() {

}
