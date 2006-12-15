#!/usr/bin/env python

from math import pi

class point(object):
    """
    Simple class that store data needed to generate reports, like
    the time that a insect stayed in the point (start_time - end_time)
    and in which areas the point is contained.
    """
        
    def __init__(self):
        self.x = None
        self.y = None
        self.start_time = None
        self.end_time = None
    
    
class track(object):
    def __init__(self):
        point_list = []
        angleSpeedQuadSum = 0
        linSpeedQuadSum = 0
        linSpeedSum = 0
        track_lenght = 0
        total_time = 0
        totalTrackSections = 0
        trackLinSpeedDeviation = 0
        trackAngleSpeedDeviation = 0
        tortuosity = 0
        meanTrackLinSpeed = 0
        meanTrackAngleSpeed = 0
    
       
class shape(object):
    """
    Abstract class. Defines basic functions needed by the video processor
    that must be implemented in derived classes.
    """
    
    def __init__(self):
        pass
    
    def contains(self, Point = None):
        pass
    
    def area(self):
        pass

    def draw(self, canvas):
        pass


class rectangle(shape):
    """
    
    """
        
    def __init__(self):
        self.x_center = None
        self.y_center = None
        self.height = None
        self.width = None
    
    def contains(self, value):
        if value.x > self.x_center + self.width / 2 :
            return False            
        elif value.x < self.x_center - self.width / 2 :
            return False
        elif value.y > self.y_center + self.height / 2 :
            return False
        elif value.y < self.y_center - self.height / 2 :
            return False
        else:
            return True
    
    def area(self):
        return self.height * self.width
    
    def draw(self, canvas, gc):
        canvas.draw_rectangle(gc, False, self.x_center - self.width/2,
                              self.y_center - self.height/2,
                              self.width, self.height)
        
                
class ellipse(shape):
    """ http://en.wikipedia.org/wiki/Ellipse#Area """
    def __init__(self):
        self.x_center = None
        self.y_center = None
        self.x_axis = None    
        self.y_axis = None
    
    def contains(self, value):
        if pow(self.x_center - value.x, 2) / pow(self.x_axis, 2) + \
            pow(self.y_center - value.y, 2) / pow(self.y_axis, 2) <= 1 :
            return True
        else:
            return False
        
    def area(self):
        return pi * self.x_axis * self.y_axis
    
    def draw(self, canvas, gc):
        canvas.draw_arc(gc, False, self.x_center - self.x_axis,
                        self.y_center - self.y_axis,
                        self.x_axis * 2, self.y_axis * 2,
                        0, 360*64)    
    
class line(shape):
    def __init__(self):
        self.x_start = None
        self.y_start = None
        self.x_end = None    
        self.y_end = None
    
    def contains(self, value):
        pass
            
    def area(self):
        return 0
    
    def draw(self, canvas, gc):
        canvas.draw_line(gc, self.x_start, self.y_start,
                             self.x_end, self.y_end)
    
class area(object):
    """
    This class represents an area. An area contains 2 attributes: 
    a shape,
    and a name, to simplify the area identification for the user.
    """
    
    def __init__(self, name=None, shape=None):
        self.shape = shape
        self.name = name
        self.track_list = []
        self.started = False
