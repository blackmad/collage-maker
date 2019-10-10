# kaleidoscope https://github.com/hugovk/pixel-tools/blob/master/kaleidoscope.py
# blue contours https://stackoverflow.com/questions/55066764/how-to-blur-feather-the-edges-of-an-object-in-an-image-using-opencv
# from PIL import Image

import subprocess
import cairo
import os
import math
import tempfile
import face_recognition
import cv2
import skimage
import numpy as np
import PIL
import PIL.Image
import sys
import dataset
import random
import pickle
from background_color_detector import BackgroundColorDetector
from colorthief import ColorThief

db = dataset.connect('sqlite:///memoize.sqlite')


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


def mirrorSurfaceAcrossY(image_surface):
    s = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, image_surface.get_width(), image_surface.get_height())
    c = cairo.Context(s)

    # invert x coordinates?
    m = cairo.Matrix(xx=-1, x0=image_surface.get_width())
    c.transform(m)
    c.set_source_surface(image_surface, 0, 0)
    c.paint()
    return s


def mirrorSurfaceAcrossX(image_surface):
    s = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, image_surface.get_width(), image_surface.get_height())
    c = cairo.Context(s)

    # invert y coordinates?
    m = cairo.Matrix(yy=-1, y0=image_surface.get_height())
    c.transform(m)
    c.set_source_surface(image_surface, 0, 0)
    c.paint()
    return s

def scaleDownRGB(rgb):
    return (rgb[0]*1.0 / 256, rgb[1]*1.0 / 256, rgb[2]*1.0 / 256)


def circleHaloImage(context, filename, scaledImage):
    colorPalette = getColorPalette(filename)

    borderColor = scaleDownRGB(colorPalette[1])
    backgroundColor = scaleDownRGB(colorPalette[0])

    fatCenterX = scaledImage.get_width() / 2
    fatCenterY = scaledImage.get_width() / 4
    fatRadius = scaledImage.get_width()

    # draw a fat border cicle
    context.set_source_rgb(*borderColor)
    context.save()
    context.scale(1, (scaledImage.get_height() / scaledImage.get_width()*0.7))
    context.arc(fatCenterX, fatCenterY, fatRadius+10, 0, math.pi*2)
    context.fill()
    context.restore()
    # draw a thin border cicle
    context.save()
    context.scale(0.75, (scaledImage.get_height() /
                         scaledImage.get_width())*0.9)
    context.arc(fatCenterX*(1/0.75), fatCenterY, fatRadius+10, 0, math.pi*2)
    context.fill()
    context.restore()

    # draw a fat background cicle
    context.set_source_rgb(*backgroundColor)
    context.save()
    context.scale(1, (scaledImage.get_height() / scaledImage.get_width()*0.7))
    context.arc(fatCenterX, fatCenterY, fatRadius, 0, math.pi*2)
    context.fill()
    context.restore()
    # draw a thin background cicle
    context.save()
    context.scale(0.75, (scaledImage.get_height() /
                         scaledImage.get_width())*0.9)
    context.arc(fatCenterX*(1/0.75), fatCenterY, fatRadius, 0, math.pi*2)
    context.fill()
    context.restore()


def ellipseHaloImage1(context, filename, scaledImage):
    colorPalette = getColorPalette(filename)

    borderColor = scaleDownRGB(colorPalette[1])
    backgroundColor = scaleDownRGB(colorPalette[0])

    fatCenterX = scaledImage.get_width() / 2
    fatCenterY = scaledImage.get_width() / 4
    fatRadius = scaledImage.get_width()

    # draw a fat border cicle
    context.set_source_rgb(*borderColor)
    context.save()
    context.scale(1, (scaledImage.get_height() / scaledImage.get_width()*0.9))
    context.arc(fatCenterX, fatCenterY, fatRadius+10, 0, math.pi*2)
    context.fill()
    context.restore()

    # draw a fat background cicle
    context.set_source_rgb(*backgroundColor)
    context.save()
    context.scale(1, (scaledImage.get_height() / scaledImage.get_width()*0.9))
    context.arc(fatCenterX, fatCenterY, fatRadius, 0, math.pi*2)
    context.fill()
    context.restore()


def makeRound(context, filename, img, centerX, centerY, numSteps, offsetRadius, offsetSteps):
    circumference = 2 * offsetRadius * math.pi
    sliceSize = max(circumference / numSteps, 25)

    average_color = getColorPalette(filename)[0]
    print(average_color)
    img = outlineImage(filename, 80, color=average_color)

    scale = sliceSize / img.get_width()
    print('scale', scale)
    print(0.25*offsetRadius / img.get_height())
    # scale = min(scale, 0.25*offsetRadius / img.get_height())
    scaledImage1 = scaleImageInPlace(img, scale)
    # scaledImage1 = mirrorSurfaceAcrossX(scaledImage1)
    scaledImage2 = mirrorSurfaceAcrossY(scaledImage1)
    scaledImages = [scaledImage1, scaledImage2]

    # context.arc(centerX, centerY, offsetRadius,
    #             0, math.pi*2)
    # context.set_source_rgb(0, 1, 0)
    # context.set_line_width(1)
    # context.stroke()

    stepSizeRads = 2*math.pi/numSteps
    for i in range(0, numSteps):
        scaledImage = scaledImages[i % len(scaledImages)]
        # context.arc(centerX, centerY, offsetRadius,
        #             (offsetSteps * stepSizeRads) + stepSizeRads*i, (offsetSteps * stepSizeRads) + stepSizeRads*i+1)
        # context.set_source_rgb(1, 0, 0)
        # context.set_line_width(1)
        # context.stroke()

        context.save()
        context.translate(centerX, centerY)
        context.rotate((offsetSteps * stepSizeRads) + (i*stepSizeRads))

        # center it in the slot
        context.translate(-scaledImage.get_width()/2, 0)
        # move it out to the circle
        context.translate(0, offsetRadius)
        # but not all the way
        # context.translate(-scaledImage.get_height()/2, 0)

        # ellipseHaloImage1(context=context, scaledImage=scaledImage, filename=filename)

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
    tmpfile = tempfile.NamedTemporaryFile(
        dir='/tmp', suffix='.png', delete=False)
    temp_file_name = tmpfile.name
    surface.write_to_png(temp_file_name)
    subprocess.call(['open', temp_file_name])


directory = '/Users/blackmad/Dropbox/Collage/All Playboy Centerfolds, 1953 - 2014/objects/person/'
size_x = 2200
size_y = 2200
files = get_files_with_extension(directory, 'png')


def resizeImageWithTransparencyNumpy(im, border=20):
  # im = cv2.imread(filename, -1)
  old_size = im.shape[:2] # old_size is in (height, width) format
  new_size = tuple([int(x+100) for x in old_size])
  im = cv2.resize(im, (new_size[1], new_size[0]))
  delta_w = new_size[1] - old_size[1]
  delta_h = new_size[0] - old_size[0]
  top, bottom = delta_h//2, delta_h-(delta_h//2)
  left, right = delta_w//2, delta_w-(delta_w//2)

  color = [0, 0, 0, 0]
  new_im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT,
      value=color)
  return new_im

def outlineImage(imgFile, border=20, color=[1, 0, 0]):
    orig_img = cv2.imread(imgFile, -1)
    resized_img = resizeImageWithTransparencyNumpy(orig_img)

    kernel = np.ones((border, border), np.uint8)
    # print(orig_img)
    
    # # "Take the array a and add 0 rows above it, 0 rows below it, 0 columns to the left of it, and 3 columns to the right of it. Fill these columns with a constant specified by constant_values".
    dilation = cv2.dilate(resized_img[:,:,3], kernel, iterations=1)

    dilation_img = cv2.imread(imgFile, -1)
    dilation_img = resizeImageWithTransparencyNumpy(dilation_img)

    dilation_img[:, :, 0] = dilation
    dilation_img[:, :, 1] = dilation
    dilation_img[:, :, 2] = dilation
    dilation_img[:, :, 3] = dilation

    mask = dilation != 0 
    print(color)
    # dilation_img[:,:,][mask] = [color[0], color[1], color[2], 0]
    # dilation_img[:,:,][mask] = [255, 0,0, 0]
    # resized_img[:,:,3][mask] = 255

    mask = dilation == 0 
    print(color)
    # transparent black - everything around the main opaque image slice
    resized_img[:,:,][mask] = [0,0,0,0]


    
    # orig_img_pil = PIL.Image.open(imgFile)
    height, width, channels = resized_img.shape
    surface = cairo.ImageSurface.create_for_data(dilation_img, cairo.FORMAT_ARGB32, width, height)
    surface2 = cairo.ImageSurface.create_for_data(resized_img, cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    
    context.set_source_surface(surface2, 0, 0)
    context.paint()
    return surface

def pil2cairo(im):
    """Transform a PIL Image into a Cairo ImageSurface."""

    # assert sys.byteorder == 'little', 'We don\'t support big endian'
    # if im.mode != 'RGBA':
    #     im = im.convert('RGBA')

    # arr = np.array(im)
    # height, width, channels = arr.shape
    # surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, width, height)
    # return surface
    tmpfile = tempfile.NamedTemporaryFile(
        dir='/tmp', suffix='.png', delete=False)
    temp_file_name = tmpfile.name
    im.save(temp_file_name)
    image_surface = cairo.ImageSurface.create_from_png(temp_file_name)
    return image_surface


def checkMemoization(filename, tableName, cb):
    table = db[tableName]
    has_face_record = table.find_one(filename=filename)
    if has_face_record:
        return pickle.loads(has_face_record['value'])
    else:
        value = cb(filename)
        table.insert(dict(filename=filename, value=pickle.dumps(value)))
        return value


def getAverageColor(filename):
    return checkMemoization(
        filename, 'average_color',
        lambda filename: ColorThief(filename).get_color(quality=3))


def getColorPalette(filename):
    return checkMemoization(filename, 'color_palette',
                            lambda filename: ColorThief(filename).get_palette(color_count=3, quality=3))


def hasFace(filename):
    return checkMemoization(filename, 'has_face', hasFaceHelper)


def hasFaceHelper(filename):
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    has_face = (face_locations is not None) and (len(face_locations) > 0)
    print('%s has face? %s' % (filename, has_face))
    return has_face


def doMain():
    radiusMoveSize = 50
    offsetRadius = 1000
    offsetSteps = 0
    ringCount = 1
    numSteps = 10
    minRadius = 50
    maxRings = 200

    # offsetRadius = 800
    # minRadius = 700

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size_x, size_y)
    context = cairo.Context(surface)

    # random.shuffle(files)

    while offsetRadius >= minRadius and ringCount < maxRings:
        filename = files.pop()

        image_surface = cairo.ImageSurface.create_from_png(filename)
        if image_surface.get_width() > image_surface.get_height():
            print('skipping, wider than tall')
            continue

        if not hasFace(filename):
            print('skipping due to no face')
            continue

        print(filename)

        makeRound(context=context, filename=filename, img=image_surface, centerX=size_x/2,
                  centerY=size_y/2, numSteps=numSteps, offsetRadius=offsetRadius, offsetSteps=offsetSteps)

        offsetRadius -= radiusMoveSize
        offsetSteps += 0.5
        ringCount += 1

        if ringCount % 3 == 0:
            numSteps *= 2
            offsetSteps = 0.5
            # offsetRadius += radiusMoveSize*1.5
        if ringCount % 3 == 1:
            numSteps = int(0.5*numSteps)
            offsetSteps = 0

    showSurface(surface)


doMain()
