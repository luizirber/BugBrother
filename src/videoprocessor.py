import Numeric

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
    
    def start_timer(self):
        pass
    
    def stop_timer(self):
        pass
    
    def elapsed_time(self):
        pass
    
    def process_video(self, source, experiment):
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
        pixbuf = pixbuf.get_from_drawable(source.Window, 
                                   source.Window.get_colormap(),
                                   0, 0, 0, 0, -1, -1)
        return True                           
        
    
    