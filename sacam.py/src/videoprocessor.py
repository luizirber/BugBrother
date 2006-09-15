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
        pass
    
    def process_video(self, source, experiment):
        
        if experiment.start_time == None:
            experiment.start_time = datetime().now()
        else:
            begin = time().now()
        
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
        pixbuf = pixbuf.get_from_drawable(source.Window, 
                                   source.Window.get_colormap(),
                                   0, 0, 0, 0, -1, -1)
        self.current = pixbuf
        
        return True                           
        
    
    