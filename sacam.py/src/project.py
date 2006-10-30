#!/usr/bin/env python

from math import pi, sqrt, acos
import cPickle
from zlib import compress, decompress

import pygtk
pygtk.require('2.0')
import gobject
import gtk.gdk

from areas import shape, point, track

class project(object):
    """
    this class contains data used to define a project.
    """
    
    attributes = {}
    refimage = None
    experiment_list = []
    filename = None
    
    def __init__(self):
        self.current_experiment = experiment()
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
    track = None
    experiment_name = None
    
    def __init__(self):
        self.threshold = 0x30
        self.release_area = [400, 400, 480, 640]
        
    def save(self):
        pass
    
    def export(self):
        # http://docs.python.org/lib/module-csv.html
        pass
    
    def prepare_point_list(self):
        #discard the points where the insect didn't 
        #move outside a defined threshold
        pass    
    
    def prepare_areas_list(self):
        for area in self.areas_list:
            for point in self.point_list:
                temp_list = []
                if area.shape.contains(point):
                    if not area.started:
                        temp_list.append(point)
                        area.started = True                    
                    else:
                        temp_list.append(point)
                else:
                    if area.started:
                        temp_track = track()
                        temp_track.point_list = temp_list
                        area.track_list.append(temp_track)
                        temp_list = []                    
                    area.started = False                    
            
    def prepare_stats(self):
        for area in areas_list:
            for track in area.point_list:
                angleSpeedQuadSum = 0
                linSpeedQuadSum = 0
                linSpeedSum = 0
                track_lenght = 0
                totalTrackSections = 0
                trackLinSpeedDeviation = 0
                trackAngleSpeedDeviation = 0
                tortuosity = 0
                meanTrackLinSpeed = 0
                meanTrackAngleSpeed = 0
                total_time = track[-1].end_time - track[0].start_time
                
                first_point = track[0]
                previous_point = track[1]
                current_point = None
                for point in track[2:] :
                    current_point = point
                    
                    temp = pow((previous_point.x - current_point.x) +
                               (previous_point.y - current_point.y), 2)
                    distancePixels = sqrt(temp)
                    distanceScaled = distancePixels / self.scale_ratio
                    linTimeDelta = current_point.end_time \
                                   - previous_point.end_time
                    linearSpeed = distanceScaled / linTimeDelta
                    linSpeedQuadSum += pow(linearSpeed, 2)
                    linSpeedSum += linearSpeed
                    track_lenght += distanceScaled
                    meanTrackLinSpeed += linearSpeed
                    totalTrackSections += 1
                    
                    angleTimeDelta = current_point.end_time \
                                     - first_point.end_time
                    angle = AngleCalc(first_point, previous_point, 
                                      current_point)
                    angleSpeed = angle / angleTimeDelta
                    angleSpeedQuadSum += pow(angleSpeed, 2)
                    angleSpeedSum += angleSpeed
                    meanTrackAngleSpeed += angleSpeed
                    totalTrackAngles += 1            

                    first_point = previous_point
                    previous_point = current_point
                    
                if totalTrackSections > 0:
                    meanTrackLinSpeed = meanTrackLinSpeed / totalTrackSections
                    trackLinSpeedDeviation = linearSpeedQuadSum - \
                                     ( pow(linSpeedSum,2)/totalTrackSections )
                    if trackLinSpeedDeviation < 0:
                        trackLinSpeedDeviation = 0
                    trackLinSpeedDeviation = \
                            trackLinSpeedDeviation / totalTrackSections
                    TrackLinSpeedDeviation = sqrt(TrackLinSpeedDeviation)
                    if totalTrackAngles > 0:
                        meanTrackAngleSpeed =  meanTrackAngleSpeed \
                                              / totalTrackAngles
                        trackAngleSpeedDeviation = angleSpeedQuadSum \
                                   - (pow(angleSpeedSum,2) / totalTrackAngles)
                        if trackAngleSpeedDeviation < 0:
                            trackAngleSpeedDeviation = 0;
                        trackAngleSpeedDeviation =  trackAngleSpeedDeviation \
                                                   /totalTrackAngles
                        trackAngleSpeedDeviation = \
                                                sqrt(trackAngleSpeedDeviation)
                    else:
                        meanTrackAngleSpeed = 0
                        trackAngleStandardDeviation = 0
                    #tortuosity
                    distance = pow(track[-1].x - track[0].x, 2) \
                               + pow(track[-1].y - track[0].y, 2)
                    distance = sqrt(distance) / scale_ratio
                    if track_lenght > 0:
                        tortuosity = 1 - distance / track_lenght
                    else:
                        tortuosity = 0
                else:
                    meanTrackLinSpeed = 0
                    meanTrackAngleSpeed = 0
                    trackLinSpeedDeviation = 0                                  
                    trackAngleSpeedDeviation = 0
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

