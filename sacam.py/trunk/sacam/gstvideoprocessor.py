''' GStreamer motion detection plugin interface for the video processor
    component of SACAM. '''

from datetime import datetime
import re

import gst

from sacam.areas import Point

class Videoprocessor(object):
    def __init__(self, name="motiondetector", output=None):
        self.detector = gst.element_factory_make(name)
        self.output = output
        self.draw = dict([("mask" , 0 ),
                          ("track", 1 ),
                          ("box"  , 0 ) ])

    def start(self, source, project):
        ''' Start the motion detection process '''
        self.detector.props.active = True
        self.detector.props.draw =   self.draw["mask"] \
                                   | self.draw["track"] << 1 \
                                   | self.draw["box"] << 2

    def stop(self, project):
        ''' Stop the motion detection process '''
        self.detector.props.active = False
        timefmt = re.compile("(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\.(\d+)")
        point_list = []

        for pnt in self.detector.props.track_list[0]:
            tmp = timefmt.search(pnt.props.start)
            args = [ int(value) for value in tmp.groups()]
            args[-1] *= 1000
            start = datetime(*args)

            tmp = timefmt.search(pnt.props.end)
            args = [int(value) for value in tmp.groups()]
            args[-1] *= 1000
            end = datetime(*args)

            new = Point(pnt.props.x_pos, pnt.props.y_pos, start, end)
            point_list.append(new)

        project.current_experiment.point_list = point_list
        self.detector.props.clear = True

    def set_detector(self, element):
        ''' Select the GStreamer element that will generate the motion
            detection data '''
        self.detector = element

    def get_detector_name(self):
        ''' Return the name of the detector '''
        return self.detector.get_factory().props.name

    def set_property(self, prop, value):
        ''' Set property value '''
        self.detector.set_property(prop, value)
        
    def set_new_tracking_area(self, x_pos, y_pos):
        ''' Set the new tracking area '''
        size = self.detector.props.size
        x0, y0 = x_pos - size/2, y_pos - size/2
        x1, y1 = x_pos + size/2, y_pos + size/2
        if x0 < 0:
          x0 = 0
        if y0 < 0:
          y0 = 0
        if x1 < 0:
          x1 = 0
        if y1 < 0:
          y1 = 0
        self.detector.props.tracking_area = [x0, y0, x1, y1]

