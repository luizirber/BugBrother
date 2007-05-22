from datetime import datetime
import re

import gst

from sacam.areas import Point

class Videoprocessor(object):
    def __init__(self, name):
        self.detector = gst.element_factory_make(name)

    def start(self, source, output, project):
        self.detector.props.active = True

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

    def set_detector(self, element):
        self.detector = element

    def get_detector_name(self):
        return self.detector.get_factory().props.name

    def set_property(self, name, value):
        self.detector.set_property(name, value)

