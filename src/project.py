#!/usr/bin/env python

from math import pi
import cPickle
from zlib import compress, decompress

import pygtk
pygtk.require('2.0')
import gobject
import gtk.gdk

from areas import shape, point

class project(object):
    """
    this class contains data used to define a project. almost all this
    attributes could be saved in and loaded from a XML file.
    """
    
    name = None
    insect_name = None
    insect_size = None
    compound_list = []
    temperature = None
    extra_attributes = {}
    refimage = None
    experiment_list = None
    filename = None
    
    def __init__(self):
        pass
    
    def save_project(self):
        temp = cPickle.dumps(self)
        proj = compress(temp)
        print self.filename
        projfile = file(self.filename,"w")
        projfile.write(proj)
        projfile.close()
    
    def load_project(self):
        projfile = file(self.filename,"r")
        temp = projfile.read()
        projfile.close()
        proj = decompress(temp)
        self = cPickle.loads(proj)
        
    
class experiment(object):
    """
    a project consist of various experiment. every experiment is an instance
    of this class. this is also saved in and loadable from a XML file.
    """
    
    point_list = []
    areas_list = []
    start_time = None
    end_time = None
    extra_attributes = {}
    measurement_unit = None
    ratio = None
    track = None
    experiment_name = None
    
    def __init__(self):
        pass
    
    def add_point(self, point):
        """
        function used by the video processor module. put a new point in the 
        point_list attribute.
        """        
        pass
    
    def get_last_point(self):
        """
        function that returns the last point inserted to make possible
        comparisons inside the video processor module.
        """
        pass
    
    def save_experiment(self):
        pass
    