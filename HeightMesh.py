from __future__ import print_function

from pyglet import image
from pyglet.gl import *

import numpy as np

class HeightMesh(object):
    def __init__(self, img):
        pic = image.load(img)
        self.cx, self.cz = pic.width, pic.height
        i = pic.get_image_data().get_data("i", -self.cx) # grab intensity
        self.data = map(ord, i) # numeric data
        
        
    def mesh(self, zero = 110):
        m = np.reshape(self.data, (self.cx, self.cz))
        
        m.tofile("data.csv", sep=",")
        
        return m
        # create the actual locations first, then construct the triangles from
        # the index
#        for x in xrange(self.cx+2):
#            for z in xrange(self.cz+2):
#                m.extend((float(x), float(self.height(x, z)), float(z)))
#                
##        t1 = numpy.array(m)
#        t1.reshape((self.cx+2, self.cz+2))
#        t1.transpose()
#        return t1.ravel()
                
    def height(self, x, z, zero = 110):
        if x in [0, self.cx+1] or z in [0, self.cz+1]:
            return 0
        else:
            return self.data[x-1 + (z-1)*self.cx] # - zero

if __name__ == '__main__':
    img = 'grayscale8x8.png'
    #def cleanmesh(img):
    n = HeightMesh(img)
    n.mesh()
#    m = n.mesh()
    
#    print(len(m))
    
#    for i in xrange(0,len(m),3):
#        if i % (n.cx+2) == 0:
#            print("")
            
#        print("  %05.1f  " % m[i+1], end="")

#    print("")
    