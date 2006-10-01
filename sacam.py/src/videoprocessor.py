import Numeric
from datetime import datetime, timedelta, time
from random import choice

import pygtk
pygtk.require('2.0')
import gtk.gdk

from areas import point

class videoprocessor(object):
    
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
            self.bug_size = 39 * self.bug_max_velocity
            #this is defined inside the experiment object
            self.current = source
            self.previous = self.current
            self.graphic = gtk.gdk.GC(output.window)
            self.graphic.set_values(line_width = 5, line_style = gtk.gdk.LINE_ON_OFF_DASH)            
            self.middle_height = (self.window[2] + self.window[0])/2            
            self.middle_width = (self.window[3] + self.window[1])/2            
            self.first_run = True
        else:
            self.previous = self.current
            self.current = source
        
        current = self.current.get_pixels_array()
        previous = self.previous.get_pixels_array()
      
        begin = datetime(1,1,1).now()
        
        size = (self.window[2] - self.window[0])/2
        if size < self.bug_size:
            size = self.bug_size
        rows_start = self.middle_height - size 
        if  rows_start < 0:
            rows_start = 0
        rows_finish = self.middle_height + size
        if rows_finish > self.current.props.height:
            rows_finish = self.current.props.height
        rows = range(rows_start, rows_finish)
                             
        size = (self.window[3] - self.window[1])/2
        if size < self.bug_size:
            size = self.bug_size
        pixels_start = self.middle_width - size 
        if pixels_start < 0:
            pixels_start = 0
        pixels_finish = self.middle_width + size
        if pixels_finish > self.current.props.width:
            pixels_finish = self.current.props.width
        pixels = range(pixels_start, pixels_finish)
        
        for row in rows:
            for pixel in pixels:
                if current[row][pixel] < (previous[row][pixel] - self.threshold) or \
                   current[row][pixel] > (previous[row][pixel] + self.threshold):
                    if self.window_is_defined:
                        self.window[2],self.window[3] = row, pixel
                    else:
                        self.window = [row,pixel,row,pixel]
                        self.window_is_defined = True
            while gtk.events_pending():
                gtk.main_iteration()
        
        self.window_is_defined = False        
        end = datetime(1,1,1).now()
        print "window:", self.window, "quantum:", end - begin        
        
        output.window.draw_pixbuf(None, self.current, 0, 0, 0, 0)
        
        output.window.draw_rectangle(self.graphic, False,         #GC, filled?
                                     pixels_start, rows_start,    #(x0,y0)
                                     pixels_finish - pixels_start,#width 
                                     rows_finish - rows_start)    #height        
        
        output.window.draw_rectangle(self.graphic, False,         #GC, filled?
                                     self.window[1], self.window[0], #(x0,y0)
                                     self.window[3] - self.window[1], #width 
                                     self.window[2] - self.window[0]) #height
        
        self.middle_width = (self.window[3] + self.window[1])/2
        self.middle_height = (self.window[2] + self.window[0])/2
        ptemp = point()
        ptemp.x, ptemp.y = self.middle_width, self.middle_height
        ptemp.start_time, ptemp.end_time = begin, end
        print ptemp.x, ptemp.y, ptemp.start_time, ptemp.end_time
#        exp.point_list.append(ptemp)     
                                              
        return True                           
