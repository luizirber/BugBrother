#!/usr/bin/env python

from math import pi, sqrt, acos
from copy import copy
import cPickle
from zlib import compress, decompress
from csv import writer

import pygtk
pygtk.require('2.0')
import gobject
import gtk.gdk

from areas import shape, point, track, rectangle, ellipse

class project(object):
    """
    this class contains data used to define a project.
    """
    
    attributes = {}
    refimage = None
    filename = None
    
    def __init__(self):
        self.experiment_list = []
        self.experiment_list.append(experiment())
        self.current_experiment = self.experiment_list[-1]
        self.bug_max_velocity = 3
        self.bug_size = 39
    
    def save(self):
        temp = cPickle.dumps(self)
        proj = compress(temp)
        print self.filename
        projfile = file(self.filename,"w")
        projfile.write(proj)
        projfile.close()
    
    def load(self):
        projfile = file(self.filename,"r")
        temp = projfile.read()
        projfile.close()
        proj = decompress(temp)
        self = cPickle.loads(proj)
    
    def export(self, filename):
        fw = writer(open(filename, 'wb'), 'excel')
        export_rows = []
        
        # write the header of the file, with info about the project
        for key in self.attributes:
            export_rows.append( (key, self.attributes[key]) )
            
        # for each experiment, collect all the data needed            
        for experiment in self.experiment_list:
            experiment_rows = experiment.export()
            for row in experiment_rows:
                export_rows.append(row)
                
        # at last, save the rows in the file
        fw.writerows(export_rows)

    
class experiment(object):
    """
    a project consist of various experiment. every experiment is an instance
    of this class.
    """
    
    point_list = []
    areas_list = []
    start_time = None
    end_time = None
    extra_attributes = {}
    measurement_unit = None
    scale_ratio = None
    x_scale_ratio = None
    y_scale_ratio = None
    track = None
    experiment_name = None
    
    def __init__(self):
        self.threshold = 0x30
        self.release_area = [0, 0, 480, 640]
        
    def save(self):
        pass
    
    def export(self):
        rows = []
        
        # for each area in the experiment, export name and shape
        for area in self.areas_list:
            rows.append( ("") )            
            if isinstance(area.shape, rectangle):
                rows.append( ("Area Name: ", area.name, "Area Shape: ", "Rectangle") )
            elif isinstance(area.shape, ellipse):
                rows.append( ("Area Name: ", area.name, "Area Shape: ", "Ellipse") )
            
            #for each track in area, export the data needed
            rows.append( ("Track List: ", "") )
            rows.append( ("", "Start Time ", "End Time ", 
                          "Residence ", "Tortuosity ", 
                          "Distance (" + self.measurement_unit + ") ", 
                          "Average Speed (" + self.measurement_unit + "/s): ", 
                          "Standard Deviation :",
                          "Angular Average Deviation :") )
            print area.track_list
            for track in area.track_list:
                rows.append( (track.start_time, track.end_time, 
                              track.end_time - track.start_time,
                              track.tortuosity, track.distance,
                              track.meanLinSpeed, track.LinSpeedDeviation,
                              track.AngleSpeedDeviation) )
            
            rows.append( ('') )
            rows.append( ("Resume: ","") )
            rows.append( ("Residence: ", 3) )
            rows.append( ("Residence (%): ", 3) )
            rows.append( ("Tortuosity: ", 4) )
            rows.append( ("Mean Distance (" + self.measurement_unit + "): ", 5) )
            rows.append( ("Total Distance (" + self.measurement_unit + "): ", 5) )            
            rows.append( ("Mean Speed (" + self.measurement_unit + "/s): ", 6) )
            rows.append( ("Standard Deviation :", 7) )
            rows.append( ("Angular Mean Deviation :", 8) )            
                
            rows.append( ('') )
            rows.append( ('') )
            
        return rows
    
    def prepare_point_list(self):
        #discard the points where the insect didn't 
        #move outside a defined threshold
        pass    
    
    def prepare_areas_list(self):
        for area in self.areas_list:
            temp_list = []            
            for point in self.point_list:
                if area.shape.contains(point):
                    if not area.started:
                        temp_list.append(point)
                        area.started = True                    
                    else:
                        temp_list.append(point)
                else:
                    if area.started:
                        temp_track = track()
                        temp_track.point_list = copy(temp_list)
                        area.track_list.append(temp_track)
                        temp_list = []
                    area.started = False  
            
    def prepare_stats(self):
        for area in self.areas_list:
            for track in area.track_list:
                track.angleSpeedQuadSum = 0
                track.linSpeedQuadSum = 0
                track.linSpeedSum = 0
                track.lenght = 0
                track.totalSections = 0
                track.LinSpeedDeviation = 0
                track.AngleSpeedDeviation = 0
                track.tortuosity = 0
                track.meanLinSpeed = 0
                track.meanAngleSpeed = 0
                track.total_time = track[-1].end_time - track[0].start_time
                
                first_point = track[0]
                previous_point = track[1]
                current_point = None
                for point in track[2:] :
                    current_point = point
                    
                    temp = pow((previous_point.x - current_point.x) +
                               (previous_point.y - current_point.y), 2)
                    track.distancePixels = sqrt(temp)
                    track.distanceScaled = track.distancePixels / self.scale_ratio
                    linTimeDelta = current_point.end_time \
                                   - previous_point.end_time
                    track.linearSpeed = track.distanceScaled / linTimeDelta
                    track.linSpeedQuadSum += pow(track.linearSpeed, 2)
                    track.linSpeedSum += track.linearSpeed
                    track.lenght += track.distanceScaled
                    track.meanLinSpeed += track.linearSpeed
                    track.totalSections += 1
                    
                    angleTimeDelta = current_point.end_time \
                                     - first_point.end_time
                    angle = AngleCalc(first_point, previous_point,
                                      current_point)
                    track.angleSpeed = angle / angleTimeDelta
                    track.angleSpeedQuadSum += pow(track.angleSpeed, 2)
                    track.angleSpeedSum += track.angleSpeed
                    track.meanAngleSpeed += track.angleSpeed
                    track.totalAngles += 1            

                    first_point = previous_point
                    previous_point = current_point
                    
                if track.totalSections > 0:
                    track.meanLinSpeed = track.meanLinSpeed/track.totalSections
                    track.LinSpeedDeviation = track.linearSpeedQuadSum - \
                              ( pow(track.linSpeedSum,2)/track.totalSections )
                    if track.LinSpeedDeviation < 0:
                        track.LinSpeedDeviation = 0
                    track.LinSpeedDeviation = track.LinSpeedDeviation \
                                              / track.totalSections
                    track.LinSpeedDeviation = sqrt(track.LinSpeedDeviation)
                    if track.totalAngles > 0:
                        track.meanAngleSpeed =  track.meanAngleSpeed \
                                              / track.totalAngles
                        track.AngleSpeedDeviation = track.angleSpeedQuadSum \
                                   - (pow(track.angleSpeedSum,2) / track.totalAngles)
                        if track.AngleSpeedDeviation < 0:
                            track.AngleSpeedDeviation = 0;
                        track.AngleSpeedDeviation =  track.AngleSpeedDeviation \
                                                   / track.totalAngles
                        track.AngleSpeedDeviation = \
                                                sqrt(track.AngleSpeedDeviation)
                    else:
                        track.meanAngleSpeed = 0
                        track.AngleStandardDeviation = 0
                    #tortuosity
                    distance = pow(track[-1].x - track[0].x, 2) \
                               + pow(track[-1].y - track[0].y, 2)
                    distance = sqrt(distance) / scale_ratio
                    if track.lenght > 0:
                        track.tortuosity = 1 - distance / track.lenght
                    else:
                        track.tortuosity = 0
                else:
                    track.meanLinSpeed = 0
                    track.meanAngleSpeed = 0
                    track.LinSpeedDeviation = 0                                  
                    track.AngleSpeedDeviation = 0
            #continua
        #mais mudancas que sejam necessarias na area
         
    def AngleCalc(self, first_point, previous_point, current_point):
        """ Calculate the angle using the Cosine Law
                         
                         first
                           +
                         /  \
                        /    \   
                     a /      \ c
                      /        \
                     / \ C      \
           previous + - - - - - +  current
                          b
        pow(c,2)  =  pow(a,2) + pow(b,2) - 2*a*b*cos(C)
          where C = angle of vertex A1
        """
        a = sqrt(  pow((first_point.x - previous_point.x), 2)
                 + pow((first_point.y - previous_point.y), 2) )
        b = sqrt(  pow((previous_point.x - current_point.x), 2)
                 + pow((previous_point.y - current_point.y), 2) )
        c = sqrt(  pow((current_point.x - first_point.x), 2)
                 + pow((current_point.y - first_point.y), 2) )
        if (a != 0) and (b != 0):
            angle = (pow(c,2) - pow(a,2) - pow(b,2)) / (-2*a*b)
            angle = acos(angle)
            angle = (angle * 180) / pi
            return (180 - angle)
        else:
            return 0

