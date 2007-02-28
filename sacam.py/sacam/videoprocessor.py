''' Provide the Videoprocessor class.

    This is the first version, implemented in Python with the Numeric module.
    It serves more like a reference implementation nowadays, because the real
    one is implemented as a C extension. '''

import Numeric
from datetime import datetime

import pygtk
pygtk.require('2.0')
import gtk.gdk

from sacam.areas import Point

class Videoprocessor(object):
    ''' Contains the motion tracking algorithm and the variables needed 
        for the computations.
    '''    
    def __init__(self):
        self.first_run = True
        self.window_is_defined = False
        self.threshold = None
        self.window = None
        self.middle_height = None
        self.middle_width = None
        self.bug_size = None
        self.graphic = None
        self.current = None
        self.previous = None
    
    def process_video(self, source, output, project):
        ''' Calculate the insect motion using a threshold difference algorithm.

            Besides that, it set correctly the experiment attributes, like
            point_list, and draw the track on the screen.
        '''
        if self.first_run:
            if project.current_experiment.start_time == None:
                project.current_experiment.start_time = datetime(1, 1, 1).now()
            tsv = project.current_experiment.threshold 
            self.threshold = Numeric.array([tsv, tsv, tsv])
            self.window = project.current_experiment.release_area            
            self.middle_height = (self.window[2] + self.window[0])/2            
            self.middle_width = (self.window[3] + self.window[1])/2            
            self.bug_size = int(project.bug_size + project.bug_max_speed)
                        
            self.graphic = gtk.gdk.GC(output.window)
            self.graphic.set_values(line_width = 5,
                                    line_style = gtk.gdk.LINE_ON_OFF_DASH)
                        
            self.current = source                        
            self.first_run = False            

            return True                        
        else:
            self.previous = self.current
            self.current = source
       
            current = self.current.get_pixels_array()
            previous = self.previous.get_pixels_array()
        
            begin = datetime(1, 1, 1).now()
            
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
            
            self.window_is_defined = False            
            
            for row in rows:
                for pixel in pixels:

                    value = previous[row][pixel] + self.threshold
                    plus_diff = current[row][pixel] > value

                    value = previous[row][pixel] - self.threshold
                    minus_diff = current[row][pixel] < value

                    if minus_diff or plus_diff:
                        if self.window_is_defined:
                            self.window[2], self.window[3] = row, pixel
                        else:
                            self.window = [row, pixel, row, pixel]
                            self.window_is_defined = True
                while gtk.events_pending():
                    gtk.main_iteration()
        
            end = datetime(1, 1, 1).now()        
            
            self.middle_width = (self.window[3] + self.window[1])/2
            self.middle_height = (self.window[2] + self.window[0])/2
            
            output.window.draw_pixbuf(None, self.current, 0, 0, 0, 0)
            
            output.window.draw_rectangle(self.graphic, False,       #GC, filled?
                                        pixels_start, rows_start,    #(x0,y0)
                                        pixels_finish - pixels_start,#width 
                                        rows_finish - rows_start)    #height
            
            output.window.draw_rectangle(self.graphic, False,       #GC, filled?
                                        self.window[1], self.window[0], #(x0,y0)
                                        self.window[3] - self.window[1], #width
                                        self.window[2] - self.window[0]) #height

            output.window.draw_rectangle(self.graphic, True,
                                 self.middle_width-3, self.middle_height-3,
                                 6, 6)                                      
        
            ptemp = Point()
            ptemp.x_pos, ptemp.y_pos = self.middle_width, self.middle_height
            ptemp.start_time, ptemp.end_time = begin, end
            project.current_experiment.point_list.append(ptemp)
                                              
        return True                           
