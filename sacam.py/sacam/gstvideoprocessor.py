from datetime import datetime
import re

import gst
import gtk

from sacam.areas import Point

class Videoprocessor(object):
    def __init__(self, name="motiondetector", output=None):
        self.detector = gst.element_factory_make(name)
        self.output = output
        self.draw = dict([("mask" , 0 ),
                          ("track", 1 ),
                          ("box"  , 0 ) ])

    def start(self, source, project):
        #TODO: set threshold, size, speed, tolerance based on project
        self.detector.props.active = True
        self.detector.props.draw =   self.draw["mask"] \
                                   | self.draw["track"] << 1 \
                                   | self.draw["box"] << 2

    def stop(self, project):
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
        self.detector = element

    def get_detector_name(self):
        return self.detector.get_factory().props.name

    def set_property(self, name, value):
        self.detector.set_property(name, value)

    def set_new_tracking_area(self, x_pos, y_pos):
        size = self.detector.props.size
        x0, y0 = x_pos - size/2, y_pos - size/2
        x1, y1 = x_pos + size/2, y_pos + size/2
        self.detector.props.tracking_area = [x0, y0, x1, y1]

