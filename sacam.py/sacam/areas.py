''' This module contains the classes that define areas, points and tracks,
    which are needed to calculate the statistics. '''

from math import pi
from lxml import etree
from datetime import datetime
from time import strptime

class Point(object):
    ''' Simple class that store data needed to generate reports.

        This includes data such as the time that a insect stayed in the 
        point (start_time - end_time) and in which areas the point 
        is contained. '''
        
    def __init__(self):
        self.x_pos = ''
        self.y_pos = ''
        self.start_time = ''
        self.end_time = ''
        
    def object_to_xml(self, points):
        ''' Convert the instance to a lxml element. '''

        new_point = etree.SubElement(points, 'point')
        
        element = etree.SubElement(new_point, "pos_x")
        element.text = str(self.x_pos)
        
        element = etree.SubElement(new_point, "pos_y")
        element.text = str(self.y_pos)
    
        element = etree.SubElement(new_point, "start_time")
        element.text = self.start_time.strftime("%Y-%m-%dT%H:%M:%S")
    
        element = etree.SubElement(new_point, "end_time")
        element.text = self.end_time.strftime("%Y-%m-%dT%H:%M:%S")

        
    def build_from_xml(self, pnt):
        ''' From a lxml element build a Point instance '''

        new_point = Point()         
        
        value = pnt.find("{http://cnpdia.embrapa.br}pos_x")
        new_point.x_pos = int(value.text)
        
        value = pnt.find("{http://cnpdia.embrapa.br}pos_y")
        new_point.y_pos = int(value.text)
        
        value = pnt.find("{http://cnpdia.embrapa.br}start_time")
        new_time = datetime(*strptime(value.text, "%Y-%m-%dT%H:%M:%S")[0:6])
        new_point.start_time = new_time
    
        value = pnt.find("{http://cnpdia.embrapa.br}end_time")
        new_time = datetime(*strptime(value.text, "%Y-%m-%dT%H:%M:%S")[0:6])
        new_point.end_time = new_time
        
        return new_point
    
    
class Track(object):
    ''' A track is defined as a path followed by the insect inside an area,
        without leaving it.

        This class contains many attributes used to calculate the statistics.'''

    def __init__(self):
        self.point_list = []
        self.lenght = 0
        self.lin_speed_deviation = 0
        self.angle_speed_deviation = 0
        self.tortuosity = 0
        self.mean_lin_speed = 0
        self.residence = 0
        self.direction_changes = 0
        self.start_time = 0
        self.end_time_time = 0
    
    def object_to_xml(self, tracks):
        ''' Convert the instance to a lxml element '''

        new_track = etree.SubElement(tracks, "track")
        
        element = etree.SubElement(new_track, "residence")
        element.text = str(self.residence)
        
        element = etree.SubElement(new_track, "tortuosity")
        element.text = str(self.tortuosity)
                
        element = etree.SubElement(new_track, "total_lenght")
        element.text = str(self.lenght)
                        
        element = etree.SubElement(new_track, "average_speed")
        element.text = str(self.mean_lin_speed)
    
        element = etree.SubElement(new_track, "standard_deviation")
        element.text = str(self.lin_speed_deviation)
    
        element = etree.SubElement(new_track, "angular_standard_deviation")
        element.text = str(self.angle_speed_deviation)                        
    
        element = etree.SubElement(new_track, "direction_changes")
        element.text = str(self.direction_changes)                        
    
        points = etree.SubElement(new_track, "points")
        for pnt in self.point_list:
            pnt.object_to_xml(points)
    
    def build_from_xml(self, trk):
        ''' Create a Track instance from a lxml element.'''

        new_track = Track()
        
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
        
        elm = trk.find("{http://cnpdia.embrapa.br}angular_standard_deviation")
        new_track.angular_standard_deviation = float(elm.text)
        
        element = trk.find("{http://cnpdia.embrapa.br}direction_changes")
        new_track.direction_changes = int(element.text)
        
        points = trk.find("{http://cnpdia.embrapa.br}points")
        for pnt in points:
            new_point = Point().build_from_xml(pnt)
            new_track.point_list.append(new_point)
       
        new_track.start_time = new_track.point_list[1].start_time
        new_track.end_time = new_track.point_list[-1].end_time
       
        return new_track
       
       
class Shape(object):
    ''' Abstract class. Defines basic functions needed by the video processor
        that must be implemented in derived classes. '''
    
    def contains(self, value):
        ''' Verify if the given point value is inside the shape. '''

        pass
    
    def area(self):
        ''' Return the area of the shape. '''

        pass

    def draw(self, canvas, graph_context):
        ''' Draw the shape in the given canvas using the given 
            graphic context.'''

        pass
    
    def object_to_xml(self, root):
        ''' Convert the instance to a lxml element '''

        pass

    def build_from_xml(self, root):
        ''' From a lxml element build a Shape instance '''

        pass


class Rectangle(Shape):
    ''' Implements a Rectangle shape, based on the shape interface. '''
        
    def __init__(self):
        super(Rectangle, self).__init__()
        self.x_center = None
        self.y_center = None
        self.height = None
        self.width = None
    
    def contains(self, value):
        ''' Verify if the given point value is inside the shape. '''

        if value.x_pos > self.x_center + self.width / 2 :
            return False            
        elif value.x_pos < self.x_center - self.width / 2 :
            return False
        elif value.y_pos > self.y_center + self.height / 2 :
            return False
        elif value.y_pos < self.y_center - self.height / 2 :
            return False
        else:
            return True
    
    def area(self):
        ''' Return the area of the shape. '''

        return self.height * self.width
    
    def draw(self, canvas, graph_context):
        ''' Draw the shape in the given canvas '''

        canvas.draw_rectangle(graph_context, False, 
                              self.x_center - self.width/2,
                              self.y_center - self.height/2,
                              self.width, self.height)
                              
    def build_from_xml(self, shp):
        ''' From a lxml element build a Rectangle instance '''

        new_shape = Rectangle()
                            
        value = shp.find("{http://cnpdia.embrapa.br}x_center")
        new_shape.x_center = int(value.text)
        
        value = shp.find("{http://cnpdia.embrapa.br}y_center")
        new_shape.y_center = int(value.text)
        
        value = shp.find("{http://cnpdia.embrapa.br}width")
        new_shape.width = int(value.text)
        
        value = shp.find("{http://cnpdia.embrapa.br}height")
        new_shape.height = int(value.text)
        
        return new_shape
                
    def object_to_xml(self, new_area):
        ''' Convert the instance to a lxml element '''

        new_shape = etree.SubElement(new_area, "rectangle")
        
        element = etree.SubElement(new_shape, "x_center")
        element.text = str(self.x_center)
        
        element = etree.SubElement(new_shape, "y_center")
        element.text = str(self.y_center)
        
        element = etree.SubElement(new_shape, "height")
        element.text = str(self.width)
        
        element = etree.SubElement(new_shape, "width")
        element.text = str(self.height)
                        
                
class Ellipse(Shape):
    ''' Implements a Ellipse based on the shape interface.

        Math formulas taken from http://en.wikipedia.org/wiki/Ellipse '''

    def __init__(self):
        super(Ellipse, self).__init__()
        self.x_center = None
        self.y_center = None
        self.x_axis = None    
        self.y_axis = None
    
    def contains(self, value):
        ''' Verify if the given point value is inside the shape. '''

        if pow(self.x_center - value.x_pos, 2) / pow(self.x_axis, 2) + \
            pow(self.y_center - value.y_pos, 2) / pow(self.y_axis, 2) <= 1 :
            return True
        else:
            return False
        
    def area(self):
        ''' Return the area of the shape. '''

        return pi * self.x_axis * self.y_axis
    
    def draw(self, canvas, graph_context):
        ''' Draw the shape in the given canvas '''

        canvas.draw_arc(graph_context, False, 
                        int(self.x_center - self.x_axis),
                        int(self.y_center - self.y_axis),
                        int(self.x_axis * 2), int(self.y_axis * 2),
                        0, 360*64)    
    
    def build_from_xml(self, shp):
        ''' From a lxml element build a Ellipse instance '''

        new_shape = Ellipse()            
        value = shp.find("{http://cnpdia.embrapa.br}x_center")
        new_shape.x_center = int(value.text)
        
        value = shp.find("{http://cnpdia.embrapa.br}y_center")
        new_shape.y_center = int(value.text)
        
        value = shp.find("{http://cnpdia.embrapa.br}x_axis")
        new_shape.x_axis = float(value.text)
        
        value = shp.find("{http://cnpdia.embrapa.br}y_axis")
        new_shape.y_axis = float(value.text)
        
        return new_shape
    
    def object_to_xml(self, new_area):
        ''' Convert the instance to a lxml element '''

        new_shape = etree.SubElement(new_area, "ellipse")
        
        element = etree.SubElement(new_shape, "x_center")
        element.text = str(self.x_center)
        
        element = etree.SubElement(new_shape, "y_center")
        element.text = str(self.y_center)
        
        element = etree.SubElement(new_shape, "x_axis")
        element.text = str(self.x_axis)
        
        element = etree.SubElement(new_shape, "y_axis")
        element.text = str(self.y_axis)
        
    
class Freeform(Shape):
    ''' Yet to implement. A poligon implementing the shape interface. '''

    def __init__(self):
        super(Freeform, self).__init__() 
        pass    
    
    def contains(self, value):
        ''' Verify if the given point value is inside the shape. '''

        pass
    
    def area(self):
        ''' Return the area of the shape. '''

        pass
    
    def draw(self, canvas, graph_context):
        ''' Draw the shape in the given canvas '''

        pass        
    
    def build_from_xml(self, shp):
        ''' From a lxml element build a Freeform instance '''

        return Freeform()
    
    def object_to_xml(self, new_area):
        ''' Convert the instance to a lxml element '''

        new_shape = etree.SubElement(new_area, "freeform")
        
        return new_shape
    
    
class Line(Shape):
    ''' A simple shape used to define scales. '''

    def __init__(self):
        super(Line, self).__init__()
        self.x_start = None
        self.y_start = None
        self.x_end = None    
        self.y_end = None
    
    def contains(self, value):
        ''' Verify if the given point value is inside the shape. '''

        pass
            
    def area(self):
        ''' Return the area of the shape. '''

        return 0
    
    def draw(self, canvas, graph_context):
        ''' Draw the shape in the given canvas '''

        canvas.draw_line(graph_context, 
                         self.x_start, self.y_start,
                         self.x_end, self.y_end)
    
    def build_from_xml(self, root):
        ''' From a lxml element build a Line instance '''

        new_shape = Line()
        
        value = root.find("{http://cnpdia.embrapa.br}x_start")
        new_shape.x_start = int(value.text)
        
        value = root.find("{http://cnpdia.embrapa.br}y_start")
        new_shape.y_start = int(value.text)
        
        value = root.find("{http://cnpdia.embrapa.br}x_end")
        new_shape.x_end = int(value.text)
        
        value = root.find("{http://cnpdia.embrapa.br}y_end")
        new_shape.y_end = int(value.text)
        
        return new_shape
    
    def object_to_xml(self, root):
        ''' Convert the instance to a lxml element '''

        new_shape = etree.SubElement(root, "line")
        
        element = etree.SubElement(new_shape, "x_start")
        element.text = str(self.x_start)
        
        element = etree.SubElement(new_shape, "y_start")
        element.text = str(self.y_start)
        
        element = etree.SubElement(new_shape, "x_end")
        element.text = str(self.x_end)
        
        element = etree.SubElement(new_shape, "y_end")
        element.text = str(self.y_end)
        
        return new_shape
    
class Area(object):
    ''' This class represents an area. '''
    
    def __init__(self, name=None, desc=None, shp=None):
        super(Area, self).__init__()
        self.shape = shp
        self.name = name
        self.description = desc
        self.track_list = []
        self.started = False
        self.number_of_tracks = ''
        self.residence_percentage = ''
        self.residence = ''
        self.total_lenght = ''
    
    def object_to_xml(self, areas):
        ''' Convert the instance to a lxml element '''

        new_area = etree.SubElement(areas, "area")
        
        self.shape.object_to_xml(new_area)
        
        element = etree.SubElement(new_area, "name")
        element.text = str(self.name)
        
        element = etree.SubElement(new_area, "description")
        element.text = str(self.description)
        
        element = etree.SubElement(new_area, "number_of_tracks")
        element.text = str(self.number_of_tracks)
        
        #TODO: this is a timedelta. build it correctly
        element = etree.SubElement(new_area, "residence")
        element.text = str(self.residence)
    
        element = etree.SubElement(new_area, "residence_percentage")
        element.text = str(self.residence_percentage)
    
        element = etree.SubElement(new_area, "total_lenght")
        element.text = str(self.total_lenght)
    
        tracks = etree.SubElement(new_area, "tracks")    
        for trk in self.track_list:
            trk.object_to_xml(tracks)
    
    def build_from_xml(self, root):
        ''' From a lxml element build a Area instance '''

        new_area = Area()
        new_shape = root.find("{http://cnpdia.embrapa.br}ellipse")
        if new_shape:
            new_area.shape = Ellipse().build_from_xml(new_shape)
        else:
            new_shape = root.find("{http://cnpdia.embrapa.br}rectangle")
            if new_shape:
                new_area.shape = Rectangle().build_from_xml(new_shape)
            else:
                new_area.shape = Freeform().build_from_xml(new_shape)
        
        element = root.find("{http://cnpdia.embrapa.br}name")
        new_area.name = element.text
        
        element = root.find("{http://cnpdia.embrapa.br}description")
        new_area.description = element.text
        
        element = root.find("{http://cnpdia.embrapa.br}number_of_tracks")
        if element.text:
            new_area.number_of_tracks = int(element.text)
        
        #TODO: this is a timedelta. build it correctly.
        element = root.find("{http://cnpdia.embrapa.br}residence")
        if element.text:
            new_area.residence = element.text
        
        element = root.find("{http://cnpdia.embrapa.br}residence_percentage")
        if element.text:
            new_area.residence_percentage = float(element.text)
        
        element = root.find("{http://cnpdia.embrapa.br}total_lenght")
        if element.text:
            new_area.total_lenght = float(element.text)
    
        tracks = root.find("{http://cnpdia.embrapa.br}tracks")
        for trk in tracks:
            new_track = Track().build_from_xml(trk)
            new_area.track_list.append(new_track)    

        return new_area

