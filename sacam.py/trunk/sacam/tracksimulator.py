import gtk
import gobject

from sacam.i18n import _

class TrackSimulator(object):

    def __init__(self, xml, project, device):
        self.project = project
        self.device = device
        self.xml = xml
        self.current_exp = project.current_experiment
        self.current_area = None

        widget = self.xml.get_widget("trackArea")
        widget.connect("expose-event", self.on_expose)

        widget = self.xml.get_widget("mainNotebook")
        widget.connect("switch-page", self.page_change_cb)

        widget = self.xml.get_widget("comboboxExperiment")
        widget.connect("changed", self.change_experiment_combo)

        widget = self.xml.get_widget("comboboxArea")
        widget.connect("changed", self.change_area_combo)

        widget = self.xml.get_widget("comboboxTrack")
        widget.connect("changed", self.change_track_combo)

    def fill_experiment_combo(self):
        combo = self.xml.get_widget("comboboxExperiment")
        model = combo.get_model()
        if model == None:
            model = gtk.ListStore(gobject.TYPE_STRING)
        model.clear()
        for exp in self.project.experiment_list:
            model.append( [exp.attributes[_("Experiment Name")]] )
        combo.set_model(model)
        self.current_exp = self.project.experiment_list[0]
        combo.set_active(0)
        combo.emit("changed")

    def fill_area_combo(self, exp):
        combo = self.xml.get_widget("comboboxArea")
        model = combo.get_model()
        if model == None:
            model = gtk.ListStore(gobject.TYPE_STRING)
        model.clear()
        for area in exp.areas_list:
            model.append( [area.name] )
        combo.set_model(model)
        self.current_area = self.current_exp.areas_list[0]
        combo.set_active(0)
        combo.emit("changed")

    def fill_track_combo(self, area):
        combo = self.xml.get_widget("comboboxTrack")
        model = combo.get_model()
        if model == None:
            model = gtk.ListStore(gobject.TYPE_STRING)
        model.clear()
        i = 0
        for track in area.track_list:
            model.append( [str(track.start_time.time())] )
            i += 1
        combo.set_model(model)
        combo.set_active(0)
        combo.emit("changed")

    def change_experiment_combo(self, widget):
        active = widget.get_active()
        exp = self.project.experiment_list[active]
        self.fill_area_combo(exp)
        self.draw_track(exp.point_list, "red")
        self.current_exp = exp

    def change_area_combo(self, widget):
        active = widget.get_active()
        area = self.current_exp.areas_list[active]
        self.fill_track_combo(area)
        self.current_area = area

    def change_track_combo(self, widget):
        active = widget.get_active()
        if self.current_area and active >= 0:
            try:
                track = self.current_area.track_list[active]
            except IndexError:
                print "erro!"
            else:
                self.draw_track(track.point_list, "blue")

    def draw_track(self, track, color_name):
        output = self.xml.get_widget("trackArea")
        points = [(point.x_pos, point.y_pos) for point in track]
        if points and output.window:
            graphic_context = gtk.gdk.GC(output.window)
            output.window.draw_pixbuf(graphic_context, self.project.refimage,
                                      0, 0, 0, 0, -1, -1,
                                      gtk.gdk.RGB_DITHER_NONE, 0, 0)
            color = gtk.gdk.color_parse(color_name)
            graphic_context.set_rgb_fg_color(color)
            output.window.draw_lines(graphic_context, points)

    def on_expose(self, wid, event):
        wid.set_size_request(self.device.frame['width'],
                             self.device.frame['height'])
        wid.window.draw_pixbuf(gtk.gdk.GC(wid.window), self.project.refimage,
                               0, 0, 0, 0, -1, -1,
                               gtk.gdk.RGB_DITHER_NONE, 0, 0)

    def page_change_cb(self, widget, page, page_num):
        if page_num == 1:
            self.fill_experiment_combo()

    def set_project(self, prj):
        self.project = prj

