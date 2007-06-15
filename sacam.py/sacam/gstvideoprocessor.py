from datetime import datetime
import re

import gst
import gtk

from sacam.areas import Point

class Videoprocessor(object):
    def __init__(self, name):
        self.detector = gst.element_factory_make(name)
        self.hdl_id = None
        self.output = None

    def start(self, source, project):
        self.detector.props.active = True
        self.detector.props.draw = 'all'
        self.output.add_events(  gtk.gdk.BUTTON_PRESS_MASK
                               | gtk.gdk.BUTTON_RELEASE_MASK
                               | gtk.gdk.BUTTON_MOTION_MASK
                               | gtk.gdk.KEY_PRESS_MASK
                               | gtk.gdk.KEY_RELEASE_MASK   )
        if self.hdl_id:
            self.output.disconnect(self.hdl_id)
        self.hdl_id = self.output.connect("button-press-event",
                                          self.output_clicked,
                                          project.bug_size,
                                          source)
        print self.output, self.hdl_id

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

    def output_clicked(self, output, event, bug_size, frame):
        print "event!"
        x0 = event.x - bug_size/2
        y0 = event.y - bug_size/2
        x1 = event.x + bug_size/2
        y1 = event.y + bug_size/2

        if x0 < 0:
            x0 = 0
        if x0 > frame['width']:
            x0 = frame['width']

        if x1 < 0:
            x1 = 0
        if x1 > frame['width']:
            x1 = frame['width']

        if y0 < 0:
            y0 = 0
        if y0 > frame['height']:
            y0 = frame['height']

        if y1 < 0:
            y1 = 0
        if y1 > frame['height']:
            y1 = frame['height']

        self.props.tracking_area = [x0, y0, x1, y1]
        print dir(self.props)#.tracking_area

