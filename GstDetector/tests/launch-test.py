import gst
import gtk
import gtk.glade

class test_program(object):
    pipeline = None
    sink = None
    detector = None
    framerate = "30/1"
    size = 30
    speed = 10
    width = 640
    height = 480
    tolerance = 10
    threshold = 100

    def expose_cb(self, area, event):
        self.sink.set_xwindow_id(area.window.xid)

    def clicked_cb(self, output, event):
        x0, y0 = event.x - self.size/2, event.y - self.size/2
        x1, y1 = event.x + self.size/2, event.y + self.size/2
        if x0 < 0: x0 = 0
        if x1 < 0: x1 = 0
        if y0 < 0: y0 = 0
        if y1 < 0: y1 = 0
        self.detector.props.tracking_area = [x0, y0, x1, y1]

    def print_list_and_exit(self, widget):
        self.detector.props.active = False
        for pnt in self.detector.props.track_list[0]:
            print "(", pnt.props.x_pos, ",", pnt.props.y_pos, ") start ", pnt.props.start, " end ", pnt.props.end
        self.pipeline.set_state(gst.STATE_NULL)
        gtk.main_quit()


    def run_pipeline(self):
#       pipeline_string = ( "v4lsrc name=source ! ffmpegcolorspace ! " \
        pipeline_string = ("videotestsrc name=source !"
                           " video/x-raw-rgb,width=%d,height=%d,framerate=%s !"
                           " motiondetector name=tracker active=true"
                           " draw=all size=%d tolerance=%d speed=%d"
                           " threshold=%d ! ximagesink name=sink") \
                           %(self.width, self.height, self.framerate,
                             self.size, self.tolerance, self.speed,
                             self.threshold)

        self.pipeline = gst.parse_launch(pipeline_string)
        self.pipeline.set_state(gst.STATE_PAUSED)

        self.source = self.pipeline.get_by_name("source")
        self.sink = self.pipeline.get_by_name("sink")
        self.detector = self.pipeline.get_by_name("tracker")
        self.detector.props.tracking_area = [ self.width/2, self.height/2,
                                              self.width/2, self.height/2 ]
#        self.source.set_norm(self.source.list_norms()[1])
#        self.source.set_channel(self.source.list_channels()[2])

        self.pipeline.set_state(gst.STATE_PLAYING)

    def activate(self, button):
        self.detector.props.active = button.get_active()

    def draw_methods(self, button):
        track = self.interface.get_widget("checkbuttonTrack").get_active()
        box = self.interface.get_widget("checkbuttonBox").get_active()
        mask = self.interface.get_widget("checkbuttonMask").get_active()

        self.detector.props.draw = mask | track << 1 | box << 2

    def set_scale(self, scale, prop):
        self.detector.set_property(prop, int(scale.get_value()))

    def connect_props(self):
        #active property
        prop = self.interface.get_widget("checkbuttonActive")
        prop.set_active(self.detector.props.active)
        prop.connect("toggled", self.activate)

        #draw property
        prop = self.interface.get_widget("checkbuttonMask")
        prop.set_active(self.detector.props.draw & (1))
        prop.connect("toggled", self.draw_methods)

        prop = self.interface.get_widget("checkbuttonTrack")
        prop.set_active(self.detector.props.draw & (1 << 1))
        prop.connect("toggled", self.draw_methods)

        prop = self.interface.get_widget("checkbuttonBox")
        prop.set_active(self.detector.props.draw & (1 << 2))
        prop.connect("toggled", self.draw_methods)

        #size property
        prop = self.interface.get_widget("scaleSize")
        prop.set_range(0, min(self.height, self.width))
        prop.set_value(self.size)
        prop.connect("value-changed", self.set_scale, "size")

        #speed property
        prop = self.interface.get_widget("scaleSpeed")
        prop.set_range(0, min(self.height, self.width))
        prop.set_value(self.speed)
        prop.connect("value-changed", self.set_scale, "speed")

        #threshold property
        prop = self.interface.get_widget("scaleThreshold")
        prop.set_value(self.threshold)
        prop.connect("value-changed", self.set_scale, "threshold")

        #tolerance property
        prop = self.interface.get_widget("scaleTolerance")
        prop.set_range(0, min(self.height, self.width))
        prop.set_value(self.tolerance)
        prop.connect("value-changed", self.set_scale, "tolerance")

    def main(self):
        self.interface = gtk.glade.XML("interface.glade")
        window = self.interface.get_widget("windowMain")
        box = self.interface.get_widget("boxMain")
        props = self.interface.get_widget("tableProps")
        draw_sink = self.interface.get_widget("drawingareaSink")
        draw_sink.set_size_request(self.width, self.height)

        self.run_pipeline()
        self.connect_props()

        draw_sink.connect("expose-event", self.expose_cb)
        draw_sink.add_events(  gtk.gdk.BUTTON_PRESS_MASK
                             | gtk.gdk.BUTTON_RELEASE_MASK
                             | gtk.gdk.BUTTON_MOTION_MASK
                             | gtk.gdk.KEY_PRESS_MASK
                             | gtk.gdk.KEY_RELEASE_MASK   )
        draw_sink.connect("button-press-event", self.clicked_cb)

        window.connect("destroy", self.print_list_and_exit)

        window.show_all()
        gtk.main()

if __name__ == "__main__":
    program = test_program()
    program.main()
