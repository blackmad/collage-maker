# kaleidoscope https://github.com/hugovk/pixel-tools/blob/master/kaleidoscope.py
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


def kindaFlipImageInPlace(img):
    scaled_img = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, img.get_width(), img.get_height())
    context = cairo.Context(scaled_img)
    context.translate(img.get_width(), img.get_height())

    context.rotate(math.pi)
    context.set_source_surface(img, 0, 0)
    context.paint()
    return scaled_img


def makeRound(context, filename, img, centerX, centerY, numSteps, offsetRadius, offsetSteps):
    circumference = 2 * offsetRadius * math.pi
    sliceSize = max(circumference / numSteps, 25)

    scale = sliceSize / img.get_width()
    scaledImage = scaleImageInPlace(img, scale)
    scaledImage = kindaFlipImageInPlace(scaledImage)

    # context.arc(centerX, centerY, offsetRadius,
    #             0, math.pi*2)
    # context.set_source_rgb(0, 1, 0)
    # context.set_line_width(1)
    # context.stroke()

    stepSizeRads = 2*math.pi/numSteps
    for i in range(0, numSteps):
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

        # this code is all for drawing the surrounding circles
        context.save()

        context.scale(1, scaledImage.get_height() / scaledImage.get_width())

        colorPalette = getColorPalette(filename)

        # the border circle
        context.arc(scaledImage.get_width()/2, scaledImage.get_width() /
                    4, scaledImage.get_width()+10, 0, math.pi*2)

        context.set_source_rgb(0, 0, 0)
        averageColor = colorPalette[1]
        context.set_source_rgb(averageColor[0]*1.0 / 256.0,
                               averageColor[1]*1.0 / 256.0,
                               averageColor[2]*1.0 / 256.0)
        context.fill()

        # the inner circle
        context.arc(scaledImage.get_width()/2, scaledImage.get_width() /
                    4, scaledImage.get_width(), 0, math.pi*2)
        context.set_source_rgb(1, 1, 1)
        averageColor = colorPalette[0]
        context.set_source_rgb(averageColor[0]*1.0 / 256.0,
                               averageColor[1]*1.0 / 256.0,
                               averageColor[2]*1.0 / 256.0)
        context.fill()

        context.restore()
        # end circle/oval code

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


def outlineImage(imgFile):
    orig_img = skimage.io.imread(imgFile)
    kernel = np.ones((20, 20), np.uint8)
    orig_img = orig_img[:, :, 3]
    dilation = cv2.dilate(orig_img, kernel, iterations=1)

    orig_img = skimage.io.imread(imgFile)
    orig_img[:, :, 0] = dilation
    orig_img[:, :, 1] = dilation
    orig_img[:, :, 2] = dilation
    orig_img[:, :, 3] = dilation

    orig_img_pil = PIL.Image.open(imgFile)
    outline_img_pil = PIL.Image.fromarray(orig_img)
    outline_img_pil.paste(orig_img_pil, mask=orig_img_pil)
    return pil2cairo(outline_img_pil)


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

    # offsetRadius = 800
    # minRadius = 700

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size_x, size_y)
    context = cairo.Context(surface)

    random.shuffle(files)

    while offsetRadius >= minRadius:
        filename = files.pop()

        image_surface = cairo.ImageSurface.create_from_png(filename)
        if image_surface.get_width() > image_surface.get_height():
            print('skipping, wider than tall')
            continue

        if not hasFace(filename):
            print('skipping due to no face')
            continue

        print(filename)
        # image_surface = outlineImage(filename)

        makeRound(context=context, filename=filename, img=image_surface, centerX=size_x/2,
                  centerY=size_y/2, numSteps=numSteps, offsetRadius=offsetRadius, offsetSteps=offsetSteps)

        offsetRadius -= radiusMoveSize
        offsetSteps += 0.5
        ringCount += 1

        if ringCount % 3 == 0:
            numSteps *= 2
            offsetSteps = 0.5
            offsetRadius += radiusMoveSize*1.5
        if ringCount % 3 == 1:
            numSteps = int(0.5*numSteps)
            offsetSteps = 0

    showSurface(surface)


doMain()
