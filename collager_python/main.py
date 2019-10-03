# kaleidoscope https://github.com/hugovk/pixel-tools/blob/master/kaleidoscope.py
# from PIL import Image

import subprocess
import cairo
import os
import math
import tempfile
import face_recognition



def get_files_with_extension(directory, extension):
    ret = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                ret.append(os.path.join(root, file))
    return ret

def scaleImageInPlace(img, scale):
    scaled_img = cairo.ImageSurface(
      cairo.FORMAT_ARGB32, int(scale*img.get_width()), int(scale*img.get_height()))

    context = cairo.Context(scaled_img)
    context.scale(scale, scale)
    context.set_source_surface(img, 0, 0)
    context.paint()
    return scaled_img

def kindaFlipImageInPlace(img):
    scaled_img = cairo.ImageSurface(
      cairo.FORMAT_ARGB32, img.get_width(), img.get_height())
    context = cairo.Context(scaled_img)
    context.translate(img.get_width(), img.get_height())

    context.rotate(math.pi)
    context.set_source_surface(img, 0, 0)
    context.paint()
    return scaled_img






def makeRound(context, img, centerX, centerY, numSteps, offsetRadius, offsetSteps):
    circumference = 2 * offsetRadius * math.pi
    sliceSize = circumference / numSteps

    scale = sliceSize / img.get_width()
    scaledImage = scaleImageInPlace(img, scale)
    scaledImage = kindaFlipImageInPlace(scaledImage)

    context.arc(centerX, centerY, offsetRadius,
                0, math.pi*2)
    context.set_source_rgb(0, 1, 0)
    context.set_line_width(1)
    context.stroke()

    stepSizeRads = 2*math.pi/numSteps
    for i in range(0, numSteps):
        context.arc(centerX, centerY, offsetRadius,
                    (offsetSteps * stepSizeRads) + stepSizeRads*i, (offsetSteps * stepSizeRads) + stepSizeRads*i+1)
        context.set_source_rgb(1, 0, 0)
        context.set_line_width(1)
        context.stroke()

        context.save()
        context.translate(centerX, centerY)
        context.rotate((offsetSteps * stepSizeRads) + (i*stepSizeRads))

        context.translate(-scaledImage.get_width()/2, 0)
        context.translate(0, offsetRadius)


        context.set_source_surface(scaledImage, 0, 0)
        context.paint()

        context.restore()        


def makeAngledMask(img, angle):
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, img.get_width(), img.get_height())

    context = cairo.Context(surface)
    context.save()
    context.rotate(angle)
    context.set_source_surface(img, 0, 0)
    context.paint()
    context.restore()

    surface_dest = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, img.get_width(), img.get_height())
    context_dest = cairo.Context(surface_dest)
    # context_dest.mask_surface (surface, 0, 0)
    context_dest.set_source_surface(img, 0, 0)
    context_dest.paint()

    context_dest.set_operator(cairo.OPERATOR_DEST_OUT)
    context_dest.set_source_surface(surface, 0, 0)
    context_dest.paint()

    # showSurface(surface_dest)

    return surface_dest


def showSurface(surface):
    tmpfile = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.png', delete=False)
    temp_file_name = tmpfile.name
    surface.write_to_png(temp_file_name)
    subprocess.call(['open', temp_file_name])


directory = '/Users/blackmad/Dropbox/Collage/All Playboy Centerfolds, 1953 - 2014/objects/person/'
size_x = 2200
size_y = 2200
files = get_files_with_extension(directory, 'png')


def doMain():
  radiusMoveSize = 25
  offsetRadius = 1000
  offsetSteps = 0
  ringCount = 1
  numSteps = 10

  surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size_x, size_y)
  context = cairo.Context(surface)

  while offsetRadius > 0:
      filename = files.pop()
      # img = Image.new('RGB', (size_x, size_y), color = 'white')
      # im = Image.open(files[0])
      # im.rotate(10, expand=True)

      image_surface = cairo.ImageSurface.create_from_png(filename)
      if image_surface.get_width() > image_surface.get_height():
        print('skipping, wider than tall')
        continue

      if check_Fa
      image = face_recognition.load_image_file(filename)
      face_locations = face_recognition.face_locations(image)
      if not face_locations or len(face_locations) == 0:
        print('skipping due to no face')
        continue

      print(filename)

      makeRound(context=context, img=image_surface, centerX=size_x/2,
                centerY=size_y/2, numSteps=numSteps, offsetRadius=offsetRadius, offsetSteps=offsetSteps)

      offsetRadius -= radiusMoveSize
      offsetSteps += 0.5
      ringCount += 1

      if ringCount % 3 == 0:
        numSteps *= 2
        offsetSteps = 0.5
      if ringCount % 3 == 1:
        numSteps = int(0.5*numSteps)
        offsetSteps = 0


  showSurface(surface)

doMain()