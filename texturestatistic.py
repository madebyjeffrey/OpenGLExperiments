
from __future__ import print_function

from pyglet import image

#from numpy import array
import numpy as np

pic = image.load('Heights.png')

width, height = pic.width, pic.height

rawimage = pic.get_image_data().get_data("i", -512)

print("Image Size: (%d, %d) length: %d \n" % (width, height, len(rawimage)))

b = map(ord, rawimage)

#b = [int(x) for x in rawimage]
a = np.array(b)

print("Min: %d, Max: %d, Mean: %d, Median: %d\n" % (a.min(), a.max(), a.mean(), np.median(a)))
#for i in rawimage:
    


