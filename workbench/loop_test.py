import Numeric

import gtk.gdk
from gtk.gdk import Pixbuf

current = Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 10, 10)
current.fill(0x22222222)
current_pixel = current.get_pixels_array()
previous = Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 10, 10)
previous.fill(0x00000000)
previous_pixel = previous.get_pixels_array()
threshold = Numeric.array([0xFF,0xFF,0xFF])

for x in range(0, current.props.width):
    for y in range(0, current.props.height):
#        print "(" + str(x) + ", " + str(y) + "): " + str(current_pixel[y][x] - previous_pixel[y][x])
        print "+: " + str((previous_pixel[y][x] + threshold).astype(Numeric.UnsignedInt8))        
        print "-: " + str((previous_pixel[y][x] - threshold).astype(Numeric.UnsignedInt8))
        if current_pixel[y][x] < (previous_pixel[y][x] - threshold).astype(Numeric.UnsignedInt8) | \
           current_pixel[y][x] > (previous_pixel[y][x] - threshold).astype(Numeric.UnsignedInt8):
            pass