''' Define the project and experiment classes. 

    A project is composed of many experiments with some common attributes.'''

import os

from math import pi, sqrt, acos
from copy import deepcopy
from csv import writer
from datetime import datetime, timedelta
from time import strptime
import re

from gtk import gdk
from kiwi.environ import environ
from lxml import etree

from sacam.i18n import _
from sacam.areas import Track, Rectangle, Ellipse, Point, Area, Line

class Project(object):
    ''' This class contains data used to define a project. '''
    
    def __init__(self):
        self.filename = ''
        self.attributes = {}
        self.refimage = ''
        self.experiment_list = []
        self.experiment_list.append(Experiment())
        self.current_experiment = self.experiment_list[-1]
        self.bug_max_speed = 3
        self.bug_size = 39
        self.attributes[_("Project Name")] = _("Project")
    
    def load(self, filename):
        ''' Given a filename open a project saved on disk.

            TODO: If returned value is None, there is an error! '''

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
            
            # Parse the file, validate, and then iterate thru it
            # to build the project instance            
            parser = etree.XMLParser(ns_clean=True)
            xml_tree = etree.parse(projfile, parser)
            if not relax_schema.validate(xml_tree):
                prj = None
                print 'error'
                # TODO: error handling
            else:
                prj = Project()
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
                prj.bug_max_speed = float(element.text)
                
                # Fifth step: experiment list
                experiments = root.find("{http://cnpdia.embrapa.br}experiments")
                prj.experiment_list = []
                for elt in experiments:
                    new_exp = Experiment().build_from_xml(elt)
                    prj.experiment_list.append(new_exp)
                if prj.experiment_list:
                    prj.current_experiment = prj.experiment_list[-1]
                    
            schemafile.close()
            # we don't need the projfile anymore, it can be closed
            projfile.close()
        return prj
            
    def save(self):
        ''' Save the current project in an xml file. '''

        projfile = file(self.filename,'w')
        projfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        
        root = etree.Element('project',
                              attrib={'xmlns':"http://cnpdia.embrapa.br"})
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
            element.text = self.refimage
        
        element = etree.SubElement(root, "bug_size")
        element.text = str(self.bug_size)
        
        element = etree.SubElement(root, "bug_max_speed")
        element.text = str(self.bug_max_speed)
        
        experiments = etree.SubElement(root, "experiments")
        for exp in self.experiment_list:
            if exp.finished:
                exp.object_to_xml(experiments)
        
        tree.write(projfile, "UTF-8", pretty_print=True)
        projfile.close()
        
    def export(self, filename):
        ''' Export the project to a CSV file '''

        filewriter = writer(open(filename, 'wb'), 'excel')
        export_rows = []
        
        # write the header of the file, with info about the project
        for key in self.attributes:
            export_rows.append( (key, self.attributes[key]) )
            
        # for each experiment, collect all the data needed            
        for exper in self.experiment_list:
            experiment_rows = exper.export()
            for row in experiment_rows:
                export_rows.append(row)
                
        # at last, save the rows in the file
        filewriter.writerows(export_rows)

    def new_experiment_from_current(self):
        ''' Creates a new experiment using the data from the current one. 
 
            The data includes areas, scales and measurement unit, but doesn't
            include points lists, for example. '''

        exp = Experiment()
        
        # TODO:take a look at this, sometimes this fails
        exp.attributes = deepcopy(self.current_experiment.attributes)
        exp.measurement_unit = deepcopy(
                                  self.current_experiment.measurement_unit)
        exp.x_scale_ratio = deepcopy(self.current_experiment.x_scale_ratio)
        exp.y_scale_ratio = deepcopy(self.current_experiment.y_scale_ratio)
        exp.threshold = deepcopy(self.current_experiment.threshold)
        exp.release_area = deepcopy(self.current_experiment.release_area)
        exp.areas_list = deepcopy(self.current_experiment.areas_list)
        
        self.experiment_list.append(exp)
        self.current_experiment = exp
    
class Experiment(object):
    ''' A project consist of many experiment. Every experiment is an instance
        of this class. '''
        
    def __init__(self):
        self.point_list = []
        self.areas_list = []
        self.start_time = ''
        self.end_time = ''
        self.attributes = {}
        self.measurement_unit = 'cm'
        self.x_scale_ratio = 1
        self.y_scale_ratio = 1
        self.scale_shape = None
        self.threshold = 0x30
        self.release_area = [0, 0, 480, 640]
        self.attributes[_("Experiment Name")] = _("Experiment")
        self.finished = False        
    
    def object_to_xml(self, experiments):
        ''' Create a lxml element from the current instance '''

        new_experiment = etree.SubElement(experiments, 'experiment')
        
        attr = etree.SubElement(new_experiment, 'attributes')
        for key in self.attributes:
            new_attribute = etree.SubElement(attr, "attribute")
            new_attribute.text = str(key + ':' + self.attributes[key])
        
        element = etree.SubElement(new_experiment, "measurement_unit")
        element.text = str(self.measurement_unit)
        
        element = etree.SubElement(new_experiment, "start_time")
        new = self.point_list[0].start_time
        element.text = new.strftime("%Y-%m-%dT%H:%M:%S") + '.' \
                       + str(new.microsecond/1000)
        
        element = etree.SubElement(new_experiment, "end_time")
        new_time = self.point_list[-1].end_time        
        element.text = new_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        element = etree.SubElement(new_experiment, "x_scale_ratio")
        element.text = str(self.x_scale_ratio)
        
        element = etree.SubElement(new_experiment, "y_scale_ratio")
        element.text = str(self.y_scale_ratio)
        
        element = etree.SubElement(new_experiment, "scale_shape")
        if self.scale_shape:
            self.scale_shape.object_to_xml(element)
        
        element = etree.SubElement(new_experiment, "threshold")
        element.text = str(self.threshold)

        element = etree.SubElement(new_experiment, "release_area")
        element.text = str(self.release_area)
        
        points = etree.SubElement(new_experiment, "points")
        for pnt in self.point_list:
            pnt.object_to_xml(points)
            
        areas = etree.SubElement(new_experiment, "areas")
        for each in self.areas_list:
            each.object_to_xml(areas)
    
    def build_from_xml(self, elt):
        ''' Create a new instance from a lxml element '''

        exp = Experiment()
        attributes = elt.find("{http://cnpdia.embrapa.br}attributes")
        for attr in attributes:
            key, value = attr.text.split(":")
            exp.attributes[key] = value
        
        element = elt.find("{http://cnpdia.embrapa.br}measurement_unit")
        exp.measurement_unit = element.text
        
        timefmt = re.compile("(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\.(\d+)")

        element = elt.find("{http://cnpdia.embrapa.br}start_time")
        tmp = timefmt.search(element.text)
        args = [int(value) for value in tmp.groups()]
        args[-1] *= 1000
        new_time = datetime(*args)
        exp.start_time = new_time
        
        element = elt.find("{http://cnpdia.embrapa.br}end_time")
        new_time = datetime(*strptime(element.text, "%Y-%m-%dT%H:%M:%S")[0:6])
        exp.end_time = new_time
        
        element = elt.find("{http://cnpdia.embrapa.br}x_scale_ratio")
        exp.x_scale_ratio = float(element.text)
        
        element = elt.find("{http://cnpdia.embrapa.br}y_scale_ratio")
        exp.y_scale_ratio = float(element.text)
        
        element = elt.find("{http://cnpdia.embrapa.br}scale_shape")
        shape_type = element.getchildren()
        if shape_type:
            if shape_type[0].tag == "{http://cnpdia.embrapa.br}line":
                exp.scale_shape = Line().build_from_xml(shape_type[0])
            elif shape_type[0].tag == "{http://cnpdia.embrapa.br}ellipse":
                exp.scale_shape = Ellipse().build_from_xml(shape_type[0])
            elif shape_type[0].tag == "{http://cnpdia.embrapa.br}rectangle":
                exp.scale_shape = Rectangle().build_from_xml(shape_type[0])
        
        element = elt.find("{http://cnpdia.embrapa.br}threshold")
        exp.threshold = int(element.text)
        
        element = elt.find("{http://cnpdia.embrapa.br}release_area")
        exp.release_area = [int(i) for i in element.text[1:-1].split(',')]
    
        points = elt.find("{http://cnpdia.embrapa.br}points")
        for pnt in points:
            new_point = Point().build_from_xml(pnt)
            exp.point_list.append(new_point)
            
        areas = elt.find("{http://cnpdia.embrapa.br}areas")
        for each in areas:
            new_area = Area().build_from_xml(each)
            exp.areas_list.append(new_area)
     
        return exp
    
    def export(self):
        ''' Export the experiment to CSV format.'''

        rows = []
        
        for key in self.attributes:
            rows.append( (key, self.attributes[key]) )
        
        # for each area in the experiment, export name and shape
        for item in self.areas_list:
            rows.append( ("") )
            rows.append( (_("Area Name: "), item.name) )
            rows.append( (_("Area Description: "), item.description) )
            if isinstance(item.shape, Rectangle):
                rows.append( (_("Area Shape: "), _("Rectangle")) )
            elif isinstance(item.shape, Ellipse):
                rows.append( (_("Area Shape: "), _("Ellipse")) )

            #for each track in area, export the data needed
            if item.track_list == []:
                string = "Insect didn't entered in this area, no data available"
                rows.append( ( _(string), "") ) 
            else:
                rows.append( (_("Track List: "), "") )                
                rows.append( ("", _("Start Time "), _("End Time "), 
                                _("Residence "), _("Tortuosity "), 
                                _("Lenght (") + self.measurement_unit + ") ", 
                                _("Average Speed (") \
                                   + self.measurement_unit + "/s): ", 
                                _("Standard Deviation :"),
                                _("Angular Average Deviation :")) )
                for trk in item.track_list:
                    rows.append( ("", trk.start_time, trk.end_time, 
                                    trk.total_time, trk.tortuosity,
                                    trk.lenght,
                                    trk.mean_lin_speed, 
                                    trk.lin_speed_deviation,
                                    trk.angle_speed_deviation) )
            
                rows.append( ('') )
                rows.append( (_("Resume: "),"") )
                rows.append( (_("Residence: "), item.residence) )
                rows.append( (_("Residence (%): "), 
                              item.residence_percentage * 100) )
                rows.append( (_("Tortuosity: "), "") )
                rows.append( (_("Average Lenght (") \
                                 + self.measurement_unit + "): ", 
                              item.total_lenght / item.number_of_tracks) )
                rows.append( (_("Total Lenght (") \
                                 + self.measurement_unit + "): ",
                              item.total_lenght) )
                
                #TODO: this value is different from the calculated in the track
                value = item.total_lenght \
                         / (float(item.residence.seconds) \
                            + float(item.residence.microseconds/1000000))
                rows.append( (_("Average Speed (") + self.measurement_unit \
                                + "/s): ",
                              value) )
    
                rows.append( (_("Standard Deviation :"), "") )
                rows.append( (_("Angular Average Deviation :"), "") )
                    
            rows.append( ('') )
            rows.append( ('') )
            
        return rows
    
    def prepare_point_list(self):
        ''' Clear the point list to speed up the stats generation.

            Discard the points where the insect didn't move inside a 
            defined threshold.'''
        pass    
    
    def prepare_areas_list(self):
        ''' Generate the tracks inside each area.'''
        for item in self.areas_list:
            temp_list = []            
            for pnt in self.point_list:
                if item.shape.contains(pnt):
                    if not item.started:
                        temp_list.append(pnt)
                        item.started = True                    
                    else:
                        temp_list.append(pnt)
                else:
                    if item.started:
                        temp_track = Track()
                        temp_track.point_list = deepcopy(temp_list)
                        item.track_list.append(temp_track)
                        temp_list = []
                    item.started = False
            #in this case, every point in point_list in inside the area
            if item.started:
                temp_track = Track()
                temp_track.point_list = deepcopy(temp_list)
                item.track_list.append(temp_track)
                temp_list = []
            
    def prepare_stats(self):
        ''' Generates the statistical data.'''
        self.start_time = self.point_list[0].start_time
        self.end_time = self.point_list[-1].end_time
        for item in self.areas_list:
            item.number_of_tracks = 0
            item.residence_percentage = 0
            item.residence = timedelta()
            item.total_lenght = 0
            for trk in item.track_list:
                trk.angleSpeedQuadSum = 0
                trk.linSpeedQuadSum = 0
                trk.linSpeedSum = 0
                trk.lenght = 0
                trk.totalSections = 0
                trk.lin_speed_deviation = 0
                trk.angle_speed_deviation = 0
                trk.tortuosity = 0
                trk.mean_lin_speed = 0
                trk.meanAngleSpeed = 0
                trk.angleSpeedSum = 0
                trk.totalAngles = 0
                trk.total_time = trk.point_list[-1].end_time - \
                                 trk.point_list[0].start_time
                trk.start_time = trk.point_list[0].start_time
                trk.end_time = trk.point_list[-1].end_time
                
                first_point = None
                previous_point = trk.point_list[0]
                current_point = None
                for pnt in trk.point_list[1:] :
                    current_point = pnt
                    
                    temp = pow((previous_point.x_pos - current_point.x_pos) +
                               (previous_point.y_pos - current_point.y_pos), 2)
                    trk.distancePixels = sqrt(temp)
                    #TODO: currently using only x_scale_ratio
                    value = float(trk.distancePixels) / self.x_scale_ratio
                    trk.distanceScaled = value

                    value = current_point.end_time - previous_point.end_time
                    lin_time_delta = value

                    seconds = float(lin_time_delta.seconds)
                    microseconds = float(lin_time_delta.microseconds)/1000000 
                    lin_time_delta = seconds + microseconds
     
                    value = float(trk.distanceScaled) / lin_time_delta
                    trk.linearSpeed = value 
                    trk.linSpeedQuadSum += pow(trk.linearSpeed, 2)
                    trk.linSpeedSum += trk.linearSpeed
                    trk.lenght += trk.distanceScaled
                    trk.mean_lin_speed += trk.linearSpeed
                    trk.totalSections += 1
                    
                    if first_point and previous_point:
                        angle_time_delta = current_point.end_time \
                                        - first_point.end_time
                        angle_time_delta = float(angle_time_delta.seconds) + \
                                    float(angle_time_delta.microseconds)/1000000
                        angle = self.angle_calc(first_point, previous_point,
                                               current_point)
                        trk.angleSpeed = float(angle) / angle_time_delta
                        trk.angleSpeedQuadSum += pow(trk.angleSpeed, 2)
                        trk.angleSpeedSum += trk.angleSpeed
                        trk.meanAngleSpeed += trk.angleSpeed
                        trk.totalAngles += 1            

                    first_point = previous_point
                    previous_point = current_point
                    
                if trk.totalSections > 0:
                    trk.mean_lin_speed /= trk.totalSections
                    trk.lin_speed_deviation = trk.linSpeedQuadSum - \
                              ( pow(trk.linSpeedSum,2)/trk.totalSections )
                    if trk.lin_speed_deviation < 0:
                        trk.lin_speed_deviation = 0
                    trk.lin_speed_deviation /= trk.totalSections
                    trk.lin_speed_deviation = sqrt(trk.lin_speed_deviation)
                    if trk.totalAngles > 0:
                        trk.meanAngleSpeed /= trk.totalAngles
                        trk.angle_speed_deviation = trk.angleSpeedQuadSum \
                              - (pow(trk.angleSpeedSum,2) / trk.totalAngles)
                        if trk.angle_speed_deviation < 0:
                            trk.angle_speed_deviation = 0;
                        trk.angle_speed_deviation /= trk.totalAngles
                        value = sqrt(trk.angle_speed_deviation)
                        trk.angle_speed_deviation = value
                    else:
                        trk.meanAngleSpeed = 0
                        trk.AngleStandardDeviation = 0
                    #tortuosity
                    sum1 = trk.point_list[-1].x_pos - trk.point_list[0].x_pos
                    sum2 = trk.point_list[-1].y_pos - trk.point_list[0].y_pos
                    value = pow(sum1, 2) + pow(sum2, 2)
                    #TODO: using x_scale_ratio only, must use y_scale_ratio too
                    distance = sqrt(value) / self.x_scale_ratio
                    if trk.lenght > 0:
                        trk.tortuosity = 1 - distance / trk.lenght
                    else:
                        trk.tortuosity = 0
                else:
                    trk.mean_lin_speed = 0
                    trk.meanAngleSpeed = 0
                    trk.lin_speed_deviation = 0 
                    trk.angle_speed_deviation = 0
                # sum up the variables to be able to calculate the resume
                item.number_of_tracks += 1
                item.residence += trk.total_time
                item.total_lenght += trk.lenght
                
            # calculate the variables of the resume
            total_time = self.end_time - self.start_time
            seconds = float(item.residence.seconds)
            microseconds =  float(item.residence.microseconds)/1000000
            total_sec = float(total_time.seconds) 
            total_micsec = float(total_time.microseconds)/1000000
            value = total_sec + total_micsec
            item.residence_percentage = (seconds + microseconds) / value
            
        # TODO: maybe some options to show the report in the screen?
         
    def angle_calc(self, first_point, previous_point, current_point):
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
        a_edge = sqrt(  pow((first_point.x_pos - previous_point.x_pos), 2)
                      + pow((first_point.y_pos - previous_point.y_pos), 2) )
        b_edge = sqrt(  pow((previous_point.x_pos - current_point.x_pos), 2)
                      + pow((previous_point.y_pos - current_point.y_pos), 2) )
        c_edge = sqrt(  pow((current_point.x_pos - first_point.x_pos), 2)
                      + pow((current_point.y_pos - first_point.y_pos), 2) )
        if (a_edge != 0) and (b_edge != 0):
            divisor = -2 * a_edge * b_edge
            angle = (pow(c_edge, 2) - pow(a_edge, 2) - pow(b_edge, 2)) / divisor
            if angle > 1:
                angle = 1
            elif angle < -1:
                angle = -1
            angle = acos(angle)
            angle = (angle * 180) / pi
            return (180 - angle)
        else:
            return 0

