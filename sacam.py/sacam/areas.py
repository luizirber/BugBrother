#!/usr/bin/env python

from math import pi
from lxml import etree

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
        
    def object_to_xml(self, points):
        new_point = etree.SubElement(points, 'point')
        
        element = etree.SubElement(new_point, "pos_x")
        element.text = str(self.x)
        
        element = etree.SubElement(new_point, "pos_y")
        element.text = str(self.y)
    
        # TODO: parse to string a datetime object
        # http://docs.python.org/lib/node85.html    
        element = etree.SubElement(new_point, "start_time")
        element.text = str('')
    
        # TODO: parse to string a datetime object
        # http://docs.python.org/lib/node85.html    
        element = etree.SubElement(new_point, "end_time")
        element.text = str('')                
        
    def build_from_xml(self, pnt):
        new_point = point()                    
        
        value = pnt.find("{http://cnpdia.embrapa.br}pos_x")
        new_point.x = int(value.text)
        
        value = pnt.find("{http://cnpdia.embrapa.br}pos_y")
        new_point.y = int(value.text)
        
        # TODO: parse the string to a datetime object
        # http://docs.python.org/lib/node85.html
        value = pnt.find("{http://cnpdia.embrapa.br}start_time")
        new_point.start_time = value.text
    
        # TODO: parse the string to a datetime object
        # http://docs.python.org/lib/node85.html
        value = pnt.find("{http://cnpdia.embrapa.br}end_time")
        new_point.end_time = value.text
        
        return new_point
    
    
class track(object):
    def __init__(self):
        self.point_list = []
        self.angleSpeedQuadSum = 0
        self.linSpeedQuadSum = 0
        self.linSpeedSum = 0
        self.track_lenght = 0
        self.total_time = 0
        self.totalTrackSections = 0
        self.trackLinSpeedDeviation = 0
        self.trackAngleSpeedDeviation = 0
        self.tortuosity = 0
        self.meanTrackLinSpeed = 0
        self.meanTrackAngleSpeed = 0
    
    def object_to_xml(self, tracks):
        new_track = etree.SubElement(tracks, "track")
        
        element = etree.SubElement(new_track, "residence")
        element.text = str(self.residence)
        
        element = etree.SubElement(new_track, "tortuosity")
        element.text = str(self.tortuosity)
                
        element = etree.SubElement(new_track, "total_lenght")
        element.text = str(self.total_lenght)
                        
        element = etree.SubElement(new_track, "average_speed")
        element.text = str(self.average_speed)                        
    
        element = etree.SubElement(new_track, "standard_deviation")
        element.text = str(self.standard_deviation)                        
    
        element = etree.SubElement(new_track, "angular_standard_deviation")
        element.text = str(self.angular_standard_deviation)                        
    
        element = etree.SubElement(new_track, "direction_changes")
        element.text = str(self.direction_changes)                        
    
        element = etree.SubElement(new_track, "points")
        for pnt in self.point_list:
            pnt.export_to_xml(points)
    
    def build_from_xml(self, trk):
        new_track = track()
        
        element = trk.find("{http://cnpdia.embrapa.br}residence")
        new_track.residence = float(element.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}tortuosity")
        new_track.tortuosity = float(element.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}total_lenght")
        new_track.total_lenght = float(element.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}average_speed")
        new_track.average_speed = float(element.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}standard_deviation")
        new_track.standard_deviation = float(element.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}angular_standard_deviation")
        new_track.angular_standard_deviation = float(element.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}direction_changes")
        new_track.direction_changes = int(element.text)
        
        points = trk.find("{http://cnpdia.embrapa.br}points")
        for pnt in points:
            new_point = point().build_from_xml(pnt)
            new_track.point_list.append(new_point)
       
        return new_track
       
       
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
    
    def object_to_xml(self, root):
        pass

    def build_from_xml(self, root):
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
                              
    def build_from_xml(self, shape):
        new_shape = rectangle()
                            
        value = shape.find("{http://cnpdia.embrapa.br}x_center")
        new_shape.x_center = int(value.text)
        
        value = shape.find("{http://cnpdia.embrapa.br}y_center")
        new_shape.y_center = int(value.text)
        
        value = shape.find("{http://cnpdia.embrapa.br}width")
        new_shape.width = int(value.text)
        
        value = shape.find("{http://cnpdia.embrapa.br}height")
        new_shape.height = int(value.text)
        
        return new_shape
                
    def object_to_xml(self, new_area):
        new_shape = etree.SubElement(new_area, "rectangle")
        
        element = etree.SubElement(new_shape, "x_center")
        element.text = str(self.x_center)
        
        element = etree.SubElement(new_shape, "y_center")
        element.text = str(self.y_center)
        
        element = etree.SubElement(new_shape, "height")
        element.text = str(self.width)
        
        element = etree.SubElement(new_shape, "width")
        element.text = str(self.height)
                        
                
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
    
    def build_from_xml(self, shape):
        new_shape = ellipse()            
        value = shape.find("{http://cnpdia.embrapa.br}x_center")
        new_shape.x_center = int(value.text)
        
        value = shape.find("{http://cnpdia.embrapa.br}y_center")
        new_shape.y_center = int(value.text)
        
        value = shape.find("{http://cnpdia.embrapa.br}x_axis")
        new_shape.x_axis = float(value.text)
        
        value = shape.find("{http://cnpdia.embrapa.br}y_axis")
        new_shape.y_axis = float(value.text)
        
        return new_shape
    
    def object_to_xml(self, new_area):
        new_shape = etree.SubElement(new_area, "ellipse")
        
        element = etree.SubElement(new_shape, "x_center")
        element.text = str(self.x_center)
        
        element = etree.SubElement(new_shape, "y_center")
        element.text = str(self.y_center)
        
        element = etree.SubElement(new_shape, "x_axis")
        element.text = str(self.x_axis)
        
        element = etree.SubElement(new_shape, "y_axis")
        element.text = str(self.y_axis)
        
    
class freeform(shape):
    def __init__(self):
        pass    
    
    def contains(self, value):
        pass
    
    def area(self):
        pass
    
    def draw(self, canvas, gc):
        pass        
    
    def build_from_xml(self, shape):
        new_shape = freeform()
        
        return new_shape
    
    
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
    
    def object_to_xml(self, areas):
        new_area = etree.SubElement(areas, "area")
        
        self.shape.object_to_xml(new_area)
        
        element = etree.SubElement(new_area, "name")
        element.text = str(self.name)
        
        element = etree.SubElement(new_area, "description")
        element.text = str(self.description)
        
        element = etree.SubElement(new_area, "number_of_tracks")
        element.text = str(self.number_of_tracks)
        
        element = etree.SubElement(new_area, "residence")
        element.text = str(self.residence)
    
        element = etree.SubElement(new_area, "residence_percentage")
        element.text = str(self.residence_percentage)
    
        element = etree.SubElement(new_area, "total_lenght")
        element.text = str(self.total_lenght)
    
        tracks = etree.SubElement(new_area, "tracks")    
        for trk in self.track_list:
            trk.object_to_xml(tracks)
    
    def build_from_xml(self, ar):
        new_area = area()
        shape = ar.find("{http://cnpdia.embrapa.br}ellipse")
        if shape:
            new_area.shape = ellipse().build_from_xml(shape)
        else:
            shape = ar.find("{http://cnpdia.embrapa.br}rectangle")
            if shape:
                new_area.shape = rectangle().build_from_xml(shape)
            else:
                new_area.shape = freeform().build_from_xml(shape)
        
        element = ar.find("{http://cnpdia.embrapa.br}name")
        new_area.name = element.text
        
        element = ar.find("{http://cnpdia.embrapa.br}description")
        new_area.description = element.text
        
        element = ar.find("{http://cnpdia.embrapa.br}number_of_tracks")
        new_area.number_of_tracks = int(element.text)
        
        element = ar.find("{http://cnpdia.embrapa.br}residence")
        new_area.residence = float(element.text)
        
        element = ar.find("{http://cnpdia.embrapa.br}residence_percentage")
        new_area.residence_percentage = float(element.text)
        
        element = ar.find("{http://cnpdia.embrapa.br}total_lenght")
        new_area.total_lenght = float(element.text)
    
        tracks = ar.find("{http://cnpdia.embrapa.br}tracks")
        for trk in tracks:
            new_track = track().build_from_xml(trk)
            new_area.track_list.append(new_track)    

        return new_area