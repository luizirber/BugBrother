import Numeric
from datetime import datetime, timedelta, time
from random import choice

import pygtk
pygtk.require('2.0')
import gtk.gdk

class videoprocessor(object):
    
    previous = None
    current = None
    threshold = None
    
    def __init__(self):
        self.first_run = False
        self.window_is_defined = False
    
    def process_video(self, source, output, experiment):
        if self.first_run == False:
#            if experiment.start_time == None:
#                experiment.start_time = datetime(1,1,1).now()
#                self.threshold = array([experiment.threshold, experiment.threshold, experiment.threshold])
#            else:
#                begin = time().now()
            self.threshold = Numeric.array([0,0,0])
            self.window = [320, 320, source.props.height, source.props.width]
#            # the first window is the liberation area
            self.window_is_defined = True
            self.bug_max_velocity = 3
            self.bug_size = 39 #* self.bug_max_velocity
            #this is defined inside the experiment object
            self.current = source
            self.previous = self.current
            self.graphic = gtk.gdk.GC(output.window)
            self.first_run = True
        else:
            self.previous = self.current
            self.current = source
            
        current = self.current.get_pixels_array()
        previous = self.previous.get_pixels_array()
        
        begin = datetime(1,1,1).now()
        middle_height = (self.window[2] + self.window[0])/2
        size = (self.window[2] - self.window[0])/2
        if size < self.bug_size:
            size = self.bug_size
        rows = range(#middle_height-size, middle_height+size) #TODO: Conferir limites
                     0, self.current.props.height)
        middle_width = (self.window[3] + self.window[1])/2
        size = (self.window[3] - self.window[1])/2
        if size < self.bug_size:
            size = self.bug_size
        pixels = range(#middle_width-size, middle_width+size) #TODO: Conferir limites
                       0, self.current.props.width)
        for row in rows:
            for pixel in pixels:
                if current[row][pixel] < (previous[row][pixel] - self.threshold) or \
                   current[row][pixel] > (previous[row][pixel] + self.threshold):
                    if window_is_defined:
                        self.window[2],self.window[3] = row, pixel
                    else:
                        self.window = [row,pixel,row,pixel]
                        self.window_is_defined = True
            while gtk.events_pending():
                gtk.main_iteration()
        
        self.window_is_defined = False        
        end = datetime(1,1,1).now()
        print "window:", self.window        
        
        output.window.draw_pixbuf(None, self.current, 0, 0, 0, 0)
        output.window.draw_rectangle(self.graphic, True,         #GC, filled?
                                     self.window[1], self.window[0], #(x0,y0)
                                     self.window[3] - self.window[1], #width 
                                     self.window[2] - self.window[0]) #height
        
#        ptemp = point()
#        ptemp.x, ptemp.y = (window[2] + window[0])/2, (window[3] + window[1])/2
#        ptemp.start_time, ptemp.end_time = begin, end
#        exp.point_list.append(ptemp)     
                                              
        return True                           
