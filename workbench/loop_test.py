import Numeric
from datetime import datetime
import gc

import gtk.gdk
from gtk.gdk import Pixbuf

def run():
    current_pixbuf = gtk.gdk.pixbuf_new_from_file("bitmap/1.bmp")
    current = current_pixbuf.get_pixels_array()
    previous_pixbuf = gtk.gdk.pixbuf_new_from_file("bitmap/1.bmp")
    previous = previous_pixbuf.get_pixels_array()
    threshold = Numeric.array([0x1,0x1,0x1])
    window = [0, 0, current_pixbuf.props.height, current_pixbuf.props.width]
    window_is_defined = True

    for i in range(2,8):
        for row in range(0, current_pixbuf.props.height):#window[0], window[2]):
            for pixel in range(0,current_pixbuf.props.width):#window[1], window[3]):
                if current[row][pixel] < (previous[row][pixel] - threshold) or \
                   current[row][pixel] > (previous[row][pixel] + threshold):
                    if window_is_defined:
                        window[2],window[3] = row, pixel
                    else:
                        window = [row,pixel,row,pixel]
                        window_is_defined = True
        
        previous = current            
        current_pixbuf = gtk.gdk.pixbuf_new_from_file("bitmap/"+str(i)+".bmp")
        current = current_pixbuf.get_pixels_array()
        print "window:", window
        window_is_defined = False        
        print "current: bitmap/"+str(i)+".bmp  previous: bitmap/"+str(i-1)+".bmp"
    gc.collect()

begin = datetime(1,1,1).now()
run()
end = datetime(1,1,1).now()
print end - begin