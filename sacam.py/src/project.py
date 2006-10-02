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
    bug_name = None
    compound_list = []
    temperature = None
    extra_attributes = {}
    refimage = None
    experiment_list = []
    filename = None
    
    def __init__(self):
        self.current_experiment = experiment()
        self.bug_max_velocity = 3
        self.bug_size = 39 
    
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
        self.threshold = 0x30
        self.liberation_area = [320, 320, 480, 640]
        
    def save_experiment(self):
        pass
    