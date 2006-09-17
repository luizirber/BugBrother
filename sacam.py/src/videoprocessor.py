import Numeric
from datetime import datetime, timedelta, time

import pygtk
pygtk.require('2.0')
import gtk.gdk

class videoprocessor(object):
    
    first = None
    previous = None
    current = None
    threshold = None
    
    def __init__(self):
        self.first_run = False
    
    def process_video(self, source, experiment):
        
        if experiment.start_time == None:
            experiment.start_time = datetime().now()
            self.threshold = array([experiment.threshold, experiment.threshold, experiment.threshold])
        else:
            begin = time().now()
        
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
        pixbuf = pixbuf.get_from_drawable(source.Window, 
                                   source.Window.get_colormap(),
                                   0, 0, 0, 0, -1, -1)
        if self.first_run == False:
            self.current = pixbuf
            self.previous = self.current
            self.first = self.previous
            self.first_run = True
        else:
            self.first = self.previous
            self.previous = self.current
            self.current = pixbuf
            
        current = self.current.get_pixels_array()
        previous = self.previous.get_pixels_array()
        first = self.first.get_pixels_array()
        
        for x in range(1, current.props.width):
            for y in range(1, current.props.height):
                if current[y][x] < (previous[y][x] - self.threshold).astype(Numeric.UnsignedInt8)) | \
                   current[y][x] > (previous[y][x] + self.threshold).astype(Numeric.UnsignedInt8)):
                    pass
                  
        return True                           
