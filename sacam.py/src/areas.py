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
    
class area(object):
    """
    This class represents an area. An area contains 3 attributes: 
    an unique identification,
    a shape,
    and a name, to simplify the area identification for the user.
    """
    
    def __init__(self):
        self.shape = None
        self.name = None
        self.point_list = []
        self.started = False
    
class shape(object):
    """
    Abstract class. Defines basic functions needed by the video processor
    that must be implemented in derived classes.
    """
    
    def __init__(self):
        pass
    
    def contains(self, Point = None):
        pass
    
    def area():
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
        
class circle(shape):
       
    def __init__(self):
        self.x_center = None
        self.y_center = None
        self.radius = None

    def contains(self, value):
        if pow(value.y - self.y_center, 2) + pow(value.x - self.x_center, 2) <= pow (self.radius, 2) :
            return True
        else:
            return False
        
    def area(self):
        return pi * pow(self.radius, 2)
        
class ellipse(shape):
        
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
    