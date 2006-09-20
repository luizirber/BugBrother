import Numeric
from datetime import datetime
import gc

import gtk.gdk
from gtk.gdk import Pixbuf

from project import experiment
from areas import point

def run(exp):
    if exp.start_time == None:
        exp.start_time = datetime(1,1,1).now()
    current_pixbuf = gtk.gdk.pixbuf_new_from_file("bitmap/1.bmp")
    current = current_pixbuf.get_pixels_array()
    previous_pixbuf = gtk.gdk.pixbuf_new_from_file("bitmap/1.bmp")
    previous = previous_pixbuf.get_pixels_array()
    threshold = Numeric.array([0x1,0x1,0x1])
    window = [0, 0, current_pixbuf.props.height, current_pixbuf.props.width]
    # the first window is the liberation area
    window_is_defined = True
    bug_max_velocity = 3
    bug_size = 39 * bug_max_velocity
    #this is defined inside the experiment object

    for i in range(2,8):
        begin = datetime(1,1,1).now()
        middle_height = (window[2] + window[0])/2
        size = (window[2] - window[0])/2
        if size < bug_size:
            size = bug_size
        rows = range(middle_height-size, middle_height+size)#0, current_pixbuf.props.height)
        middle_width = (window[3] + window[1])/2
        size = (window[3] - window[1])/2
        if size < bug_size:
            size = bug_size
        pixels = range(middle_width-size, middle_width+size)#0, current_pixbuf.props.width)
        for row in rows:
            for pixel in pixels:
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
        end = datetime(1,1,1).now()
        print "quantum:", end - begin
        ptemp = point()
        ptemp.x, ptemp.y, ptemp.start_time = (window[2] + window[0])/2, (window[3] + window[1])/2, end
        exp.point_list.append(ptemp)     
    gc.collect()
    exp.end_time = datetime(1,1,1).now()

if __name__ == '__main__':
    exper = experiment()
    begin = datetime(1,1,1).now()
    run(exper)
    end = datetime(1,1,1).now()
    print end - begin    
    exper.process()
    