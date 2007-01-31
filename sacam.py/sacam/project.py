#!/usr/bin/env python

import os

from math import pi, sqrt, acos
from copy import deepcopy
import cPickle
from csv import writer
from datetime import timedelta

from gtk import gdk
from kiwi.environ import environ
from lxml import etree

from sacam.i18n import _
from sacam.areas import track, rectangle, ellipse, point, area, freeform

class project(object):
    """
    this class contains data used to define a project.
    """
    
    def __init__(self):
        self.filename = None
        self.attributes = {}
        self.refimage = None
        self.experiment_list = []
        self.experiment_list.append(experiment())
        self.current_experiment = self.experiment_list[-1]
        self.bug_max_speed = 3
        self.bug_size = 39
        self.refimage = None
        self.attributes[_("Project Name")] = _("Project")
    
    def load(self, filename):
        ''' TODO: If returned value is None, there is an error! '''
        prj = None
        try:
            #open the file for reading
            projfile = file(filename, "r")
        except:
            pass
        else:
            schemafile = open(environ.find_resource('xml','sacam.rng'))
            schema = etree.parse(schemafile)
            relax_schema = etree.RelaxNG(schema)
            
            ## Parse the file, validate, and then iterate thru it
            ## to build the project instance            
            parser = etree.XMLParser(ns_clean=True)
            xml_tree = etree.parse(projfile, parser)
            if not relax_schema.validate(xml_tree):
                prj = None
                print error
                # TODO: error handling
            else:
                prj = project()
                prj.filename = filename
                
                # get the <project> tag
                root = xml_tree.getroot()
                
                # begin parsing of tree.
                # First step: build the attributes dictionary.
                element = root.find("{http://cnpdia.embrapa.br}attributes")
                for attr in element:
                    key, value = attr.text.split(':')
                    prj.attributes[key] = value
                
                # Second step: refimage property
                element = root.find("{http://cnpdia.embrapa.br}refimage")
                fln, tail = os.path.split(element.text)
                prj.refimage = gdk.pixbuf_new_from_file(fln + '/refimg.jpg')
                
                # Third step: bug_size property
                element = root.find("{http://cnpdia.embrapa.br}bug_size")
                prj.bug_size = float(element.text)
                
                # Fourth step: bug_max_speed property
                element = root.find("{http://cnpdia.embrapa.br}bug_max_speed")
                prj.bug_speed = float(element.text)
                
                # Fifth step: experiment list
                experiments = root.find("{http://cnpdia.embrapa.br}experiments")
                prj.experiment_list = []
                for el in experiments:
                    new_exp = experiment().build_from_xml(el)
                    prj.experiment_list.append(new_exp)
                prj.current_experiment = prj.experiment_list[-1]
                    
            schemafile.close()
            # we don't need the projfile anymore, it can be closed
            projfile.close()
        return prj
            
    def save(self):
        projfile = file(self.filename,'w')
        projfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        
        root = etree.Element('project',attrib={'xmlns':"http://cnpdia.embrapa.br"})
        tree = etree.ElementTree(root)
        
        attr = etree.SubElement(root, "attributes")
        for key in self.attributes:
            new_attribute = etree.SubElement(attr, "attribute")
            new_attribute.text = str(key + ':' + self.attributes[key])
        
        element = etree.SubElement(root, "refimage")
        if self.refimage:
            element.text = self.filename
            fln, tail = os.path.split(element.text)
            self.refimage.save(fln + '/refimg.jpg', "jpeg", {"quality":"80"})
        else:
            element.text = ''
        
        element = etree.SubElement(root, "bug_size")
        element.text = str(self.bug_size)
        
        element = etree.SubElement(root, "bug_max_speed")
        element.text = str(self.bug_max_speed)
        
        experiments = etree.SubElement(root, "experiments")
        for exp in self.experiment_list:
            exp.object_to_xml(experiments)
        
        tree.write(projfile,"UTF-8",pretty_print=True)
        projfile.close()
        
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

    def new_experiment_from_current(self):
        exp = experiment()
        
        # TODO:take a look at this
        exp.attributes = deepcopy(self.current_experiment.attributes)
        exp.measurement_unit = deepcopy(self.current_experiment.measurement_unit)
        exp.x_scale_ratio = deepcopy(self.current_experiment.x_scale_ratio)
        exp.y_scale_ratio = deepcopy(self.current_experiment.y_scale_ratio)
        exp.threshold = deepcopy(self.current_experiment.threshold)
        exp.release_area = deepcopy(self.current_experiment.release_area)
        exp.areas_list = deepcopy(self.current_experiment.areas_list)
        
        self.experiment_list.append(exp)
        self.current_experiment = exp
    
class experiment(object):
    """
    a project consist of various experiment. every experiment is an instance
    of this class.
    """
    
    point_list = []
    areas_list = []
    start_time = None
    end_time = None
    attributes = {}
    measurement_unit = 'cm'
    x_scale_ratio = '1'
    y_scale_ratio = '1'
    
    def __init__(self):
        self.threshold = 0x30
        self.release_area = [0, 0, 480, 640]
        self.attributes[_("Experiment Name")] = _("Experiment")
    
    def object_to_xml(self, experiments):
        new_experiment = etree.SubElement(experiments, 'experiment')
        
        attr = etree.SubElement(new_experiment, 'attributes')
        for key in self.attributes:
            new_attribute = etree.SubElement(attr, "attribute")
            new_attribute.text = str(key + ':' + self.attributes[key])
        
        element = etree.SubElement(new_experiment, "measurement_unit")
        element.text = str(self.measurement_unit)
        
        # TODO: parse to string a datetime object
        # http://docs.python.org/lib/node85.html
        element = etree.SubElement(new_experiment, "start_time")
        element.text = str('start_time')
        
        # TODO: parse to string a datetime object
        # http://docs.python.org/lib/node85.html
        element = etree.SubElement(new_experiment, "end_time")
        element.text = str('end_time')
        
        element = etree.SubElement(new_experiment, "x_scale_ratio")
        element.text = str(self.x_scale_ratio)
        
        element = etree.SubElement(new_experiment, "y_scale_ratio")
        element.text = str(self.y_scale_ratio)
        
        element = etree.SubElement(new_experiment, "threshold")
        element.text = str(self.threshold)

        # TODO: save the name of the release area
        element = etree.SubElement(new_experiment, "release_area")
        element.text = str('')
        
        points = etree.SubElement(new_experiment, "points")
        for pnt in self.point_list:
            pnt.object_to_xml(points)
            
        areas = etree.SubElement(new_experiment, "areas")
        for ar in self.areas_list:
            ar.object_to_xml(areas)
    
    
    def build_from_xml(self, el):
        exp = experiment()
        attributes = el.find("{http://cnpdia.embrapa.br}attributes")
        for attr in attributes:
            key, value = attr.text.split(":")
            exp.attributes[key] = value
        
        element = el.find("{http://cnpdia.embrapa.br}measurement_unit")
        exp.measurement_unit = element.text
        
        # TODO: parse the string to a datetime object
        # http://docs.python.org/lib/node85.html
        element = el.find("{http://cnpdia.embrapa.br}start_time")
        exp.start_time = element.text
        
        # TODO: parse the string to a datetime object
        # http://docs.python.org/lib/node85.html
        element = el.find("{http://cnpdia.embrapa.br}end_time")
        exp.end_time = element.text
        
        element = el.find("{http://cnpdia.embrapa.br}x_scale_ratio")
        exp.x_scale_ratio = float(element.text)
        
        element = el.find("{http://cnpdia.embrapa.br}y_scale_ratio")
        exp.y_scale_ratio = float(element.text)
        
        element = el.find("{http://cnpdia.embrapa.br}threshold")
        exp.threshold = int(element.text)
        
        # TODO: make a acessor function to set release_area
        # it should take a string, and search an area_name
        # that matches this string.
        #element = el.find("{http://cnpdia.embrapa.br}release_area")
        #exp.set_release_area(element.text)
    
        points = el.find("{http://cnpdia.embrapa.br}points")
        for pnt in points:
            new_point = point().build_from_xml(pnt)
            exp.point_list.append(new_point)
            
        areas = el.find("{http://cnpdia.embrapa.br}areas")
        for ar in areas:
            new_area = area().build_from_xml(ar)
            exp.areas_list.append(new_area)
        return exp
    
    def build_xml(self):
        pass
    
    def export(self):
        rows = []
        
        for key in self.attributes:
            rows.append( (key, self.attributes[key]) )
        
        # for each area in the experiment, export name and shape
        for area in self.areas_list:
            rows.append( ("") )
            if isinstance(area.shape, rectangle):
                rows.append( (_("Area Name: "), area.name) )
                rows.append( (_("Area Shape: "), _("Rectangle")) )
            elif isinstance(area.shape, ellipse):
                rows.append( (_("Area Name: "), area.name) )
                rows.append( (_("Area Shape: "), _("Ellipse")) )
            
            #for each track in area, export the data needed
            if area.track_list == []:
                rows.append( (_("Insect didn't entered in this area, no data available"), "") )
            else:
                rows.append( (_("Track List: "), "") )                
                rows.append( ("", _("Start Time "), _("End Time "), 
                                _("Residence "), _("Tortuosity "), 
                                _("Lenght (") + self.measurement_unit + ") ", 
                                _("Average Speed (") + self.measurement_unit + "/s): ", 
                                _("Standard Deviation :"),
                                _("Angular Average Deviation :")) )
                for track in area.track_list:
                    rows.append( ("", track.start_time, track.end_time, 
                                    track.total_time, track.tortuosity,
                                    track.lenght,
                                    track.meanLinSpeed, 
                                    track.LinSpeedDeviation,
                                    track.AngleSpeedDeviation) )
            
                rows.append( ('') )
                rows.append( (_("Resume: "),"") )
                rows.append( (_("Residence: "), area.residence) )
                rows.append( (_("Residence (%): "), area.residence_percentage * 100) )
                rows.append( (_("Tortuosity: "), "") )
                rows.append( (_("Average Lenght (") + self.measurement_unit + "): ", 
                                area.total_lenght / area.number_of_tracks) )
                rows.append( (_("Total Lenght (") + self.measurement_unit + "): ", area.total_lenght) )
                
                #TODO: this value is different from the calculated in the track. Hum.
         		#TODO2: division by zero! verify
                value = area.total_lenght / \
                        (float(area.residence.seconds) + float(area.residence.microseconds/1000000))
                rows.append( (_("Average Speed (") + self.measurement_unit + "/s): ", value) )
    
                rows.append( (_("Standard Deviation :"), "") )
                rows.append( (_("Angular Average Deviation :"), "") )            
                    
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
                        temp_track.point_list = deepcopy(temp_list)
                        area.track_list.append(temp_track)
                        temp_list = []
                    area.started = False
            #in this case, every point in point_list in inside the area
            if area.started:
                temp_track = track()
                temp_track.point_list = deepcopy(temp_list)
                area.track_list.append(temp_track)
                temp_list = []
            
    def prepare_stats(self):
        self.start_time = self.point_list[0].start_time
        self.end_time = self.point_list[-1].end_time
        for area in self.areas_list:
            area.number_of_tracks = 0
            area.residence_percentage = 0
            area.residence = timedelta()
            area.total_lenght = 0
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
                track.angleSpeedSum = 0
                track.totalAngles = 0
                track.total_time = track.point_list[-1].end_time - track.point_list[0].start_time
                track.start_time = track.point_list[0].start_time
                track.end_time = track.point_list[-1].end_time
                
                first_point = None
                previous_point = track.point_list[0]
                current_point = None
                for point in track.point_list[1:] :
                    current_point = point
                    
                    temp = pow((previous_point.x - current_point.x) +
                               (previous_point.y - current_point.y), 2)
                    track.distancePixels = sqrt(temp)
                    #TODO: currently using only x_scale_ratio
                    track.distanceScaled = float(track.distancePixels) / self.x_scale_ratio
                    linTimeDelta = current_point.end_time - previous_point.end_time
                    linTimeDelta = float(linTimeDelta.seconds) + float(linTimeDelta.microseconds)/1000000
                    track.linearSpeed = float(track.distanceScaled) / linTimeDelta
                    track.linSpeedQuadSum += pow(track.linearSpeed, 2)
                    track.linSpeedSum += track.linearSpeed
                    track.lenght += track.distanceScaled
                    track.meanLinSpeed += track.linearSpeed
                    track.totalSections += 1
                    
                    if first_point and previous_point:                    
                        angleTimeDelta = current_point.end_time \
                                        - first_point.end_time
                        angleTimeDelta = float(angleTimeDelta.seconds) + \
                                         float(angleTimeDelta.microseconds)/1000000
                        angle = self.AngleCalc(first_point, previous_point,
                                                current_point)
                        track.angleSpeed = float(angle) / angleTimeDelta
                        track.angleSpeedQuadSum += pow(track.angleSpeed, 2)
                        track.angleSpeedSum += track.angleSpeed
                        track.meanAngleSpeed += track.angleSpeed
                        track.totalAngles += 1            

                    first_point = previous_point
                    previous_point = current_point
                    
                if track.totalSections > 0:
                    track.meanLinSpeed /= track.totalSections
                    track.LinSpeedDeviation = track.linSpeedQuadSum - \
                              ( pow(track.linSpeedSum,2)/track.totalSections )
                    if track.LinSpeedDeviation < 0:
                        track.LinSpeedDeviation = 0
                    track.LinSpeedDeviation /= track.totalSections
                    track.LinSpeedDeviation = sqrt(track.LinSpeedDeviation)
                    if track.totalAngles > 0:
                        track.meanAngleSpeed /= track.totalAngles
                        track.AngleSpeedDeviation = track.angleSpeedQuadSum \
                                   - (pow(track.angleSpeedSum,2) / track.totalAngles)
                        if track.AngleSpeedDeviation < 0:
                            track.AngleSpeedDeviation = 0;
                        track.AngleSpeedDeviation /= track.totalAngles
                        track.AngleSpeedDeviation = \
                                                sqrt(track.AngleSpeedDeviation)
                    else:
                        track.meanAngleSpeed = 0
                        track.AngleStandardDeviation = 0
                    #tortuosity
                    distance = pow(track.point_list[-1].x - track.point_list[0].x, 2) \
                               + pow(track.point_list[-1].y - track.point_list[0].y, 2)
                    #TODO: using x_scale_ratio only, must use y_scale_ratio too
                    distance = sqrt(distance) / self.x_scale_ratio
                    if track.lenght > 0:
                        track.tortuosity = 1 - distance / track.lenght
                    else:
                        track.tortuosity = 0
                else:
                    track.meanLinSpeed = 0
                    track.meanAngleSpeed = 0
                    track.LinSpeedDeviation = 0                                  
                    track.AngleSpeedDeviation = 0
                # sum up the variables to be able to calculate the resume
                area.number_of_tracks += 1
                area.residence += track.total_time
                area.total_lenght += track.lenght
                
            # calculate the variables of the resume
            total_time = self.end_time - self.start_time
            area.residence_percentage = \
                   (float(area.residence.seconds) + float(area.residence.microseconds)/1000000) / \
                   (float(total_time.seconds) + float(total_time.microseconds)/1000000)
            
        # TODO: maybe some options to show the report in the screen?
         
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
            if angle > 1:
                angle = 1
            elif angle < -1:
                angle = -1
            angle = acos(angle)
            angle = (angle * 180) / pi
            return (180 - angle)
        else:
            return 0

