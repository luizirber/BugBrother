from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from sacam.areas import Ellipse, Rectangle, Area, Line

from sacam.i18n import _

class AreasDiag(object):
    ''' This dialog contains the code necessary to create areas for the
        experiment.

        It contains the code to move the areas and save them in the experiment,
        too. '''

    def __init__(self, project, xml):
        self.xml = xml
        self.project = project
        self.output_handler = None

        # widgets to be used
        output = self.xml.get_widget("drawingareaAreas")
        area_name = self.xml.get_widget("entryAreaName")
        area_desc = self.xml.get_widget("entryAreaDesc")
        self.window = None

        # setting up the areas treeview
        view = self.xml.get_widget("treeviewAreas")

        # model columns: area name, area shape, area description
        model = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING)
        view.set_model(model)

        # renderer of the first column
        renderer = gtk.CellRendererText()
        renderer.props.editable = True
        renderer.connect("edited", self.edited_cb, area_name,
                          view.get_model(), 0)
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        view.append_column(column)

        # renderer of the second column
        renderer = gtk.CellRendererText()
        renderer.props.editable = True
        renderer.connect("edited", self.edited_cb, area_desc,
                          view.get_model(), 2)
        column = gtk.TreeViewColumn(_("Description"), renderer, text=2)
        view.append_column(column)

        # To treat single selection only
        selection = view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        view.connect("cursor_changed", self.select_area, output,
                      area_name, area_desc)

        #connecting the callbacks of the areasDiag
        widget = self.xml.get_widget("buttonAddArea")
        widget.connect("clicked", self.shape_action, "add")

        widget = self.xml.get_widget("buttonRemoveArea")
        widget.connect("clicked", self.remove_area)

        widget = self.xml.get_widget("buttonResizeArea")
        widget.connect("clicked", self.shape_action, "resize")

        widget = self.xml.get_widget("buttonMoveArea")
        widget.connect("clicked", self.shape_action, "move")

        #buttons to define the shape that will be drawn
        widget = self.xml.get_widget("buttonRectangle")
        widget.connect("clicked", self.set_shape, "rectangle")

        widget = self.xml.get_widget("buttonEllipse")
        widget.connect("clicked", self.set_shape, "ellipse")

        widget = self.xml.get_widget("buttonSetReleaseArea")
        widget.connect("clicked", self.set_as_release_area)
        self.release_area = None

        #default shape to be drawn
        self.shape_type = "rectangle"

        #default action is to add an area
        self.action = "add"
        self.composing_shape = False
        self.moving_shape_started = False
        self.resizing_shape_started = False
        self.graphic_context = None
        self.red_gc = None

        self.start_point = None
        self.end_point = None
        self.first_point = None
        self.last_point = None
        self.initial_point = None
        self.final_point = None
        self.selected_shape = None
        self.resizing_shape = None
        self.temp_shape = None
        self.moving_shape = None

        output.add_events(  gtk.gdk.BUTTON_PRESS_MASK
                          | gtk.gdk.BUTTON_RELEASE_MASK
                          | gtk.gdk.BUTTON_MOTION_MASK
                          | gtk.gdk.KEY_PRESS_MASK
                          | gtk.gdk.KEY_RELEASE_MASK   )
        #these three are necessary to draw something in the draw area
        output.connect("button-press-event", self.compose_shape)
        output.connect("motion-notify-event", self.compose_shape)
        output.connect("button-release-event", self.finish_shape,
                        model, area_name, area_desc, view)

    def edited_cb(self, cell, path, new_text, edit_view, model, column):
        ''' Callback function. Set the edit_view to have the same text as
            the model'''

        model[path][column] = new_text
        edit_view.set_text(new_text)

    def run(self, wid, project, interface):
        ''' Run the specific dialog and save the changes in the project. '''

        self.project = project
        model = self.xml.get_widget("treeviewAreas").get_model()
        output = self.xml.get_widget("drawingareaAreas")
        output.set_size_request(project.refimage.props.width,
                                project.refimage.props.height)
        if self.output_handler:
            output.disconnect(self.output_handler)
        self.output_handler = output.connect("expose_event", self.draw_expose,
                                             self.project, model)
        self.window = self.xml.get_widget("dialogAreas");
        self.window.show_all()

        model.clear()
        for each_area in project.current_experiment.areas_list:
            value = (each_area.name, each_area.shape, each_area.description)
            model.append(value)

        response = self.window.run()
        if response == gtk.RESPONSE_OK :
            # read the areas from the treemodel and save in the
            # current experiment areas list
            values = [ (r[0], r[1], r[2]) for r in model ]
            project.current_experiment.areas_list = []
            for name, shape, desc in values:
                new_area = Area(name, desc, shape)
                project.current_experiment.areas_list.append(new_area)

            # set the release_area attribute of the current experiment
            release = self.release_area.get_bounds()
            self.project.current_experiment.release_area = release

            self.window.hide_all()
            interface.update_state()
            return True
        else:
            self.window.hide_all()
            interface.update_state()
            return False

    def set_as_release_area(self, wid):
        ''' Set the current selected shape as the release area. '''

        if self.selected_shape != None:
            self.release_area = self.selected_shape
        else:
            diag = gtk.MessageDialog ( self.window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         gtk.MESSAGE_ERROR,
                         gtk.BUTTONS_OK,
                         _("An area must be selected") )
            diag.run()
            diag.destroy()

    def select_area(self, wid, output, area_name, area_desc):
        ''' Select an area in the treeview to be changed. '''

        selection = wid.get_selection()
        treemodel, treeiter = selection.get_selected()
        self.selected_shape = treemodel.get_value(treeiter, 1)
        area_name.set_text(treemodel.get_value(treeiter, 0))
        area_desc.set_text(treemodel.get_value(treeiter, 2))
        if self.red_gc == None:
            color = gtk.gdk.color_parse("red")
            self.red_gc = output.window.new_gc()
            self.red_gc.set_rgb_fg_color(color)
        self.selected_shape.draw(output.window, self.red_gc)
        output.queue_draw()

    def set_shape(self, wid, shape_type):
        ''' Set shape with one of the valid values. '''

        self.shape_type = shape_type

    def compose_shape(self, wid, event):
        ''' The rather big function that does it all.

            It verifies if the shaping is being first drawed, or being moved,
            or being resized. Based on that it does the necessary stuff. '''
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)
        if self.action == "add":
            if self.composing_shape == False:
                self.composing_shape = True
                if self.shape_type == "rectangle":
                    self.temp_shape = Rectangle()
                elif self.shape_type == "ellipse":
                    self.temp_shape = Ellipse()
                self.start_point = (event.x, event.y)
            else:
                self.end_point = (event.x, event.y)
                if self.shape_type == "rectangle":
                    value = int(abs(self.end_point[0] - self.start_point[0]))
                    self.temp_shape.width = value

                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.temp_shape.height = self.temp_shape.width
                    else:
                        value = abs(self.end_point[1] - self.start_point[1])
                        self.temp_shape.height = int(value)
                    #Static center
#                    self.temp_shape.x_center = int(self.start_point[0])
#                    self.temp_shape.y_center = int(self.start_point[1])
                    #Moving center
                    if self.start_point[0] < self.end_point[0]:
                        value = self.start_point[0] + self.temp_shape.width/2
                        self.temp_shape.x_center = int(value)
                    else:
                        value = self.end_point[0] + self.temp_shape.width/2
                        self.temp_shape.x_center = int(value)
                    if self.start_point[1] < self.end_point[1]:
                        value = self.start_point[1] + self.temp_shape.height/2
                        self.temp_shape.y_center = int(value)
                    else:
                        value = self.end_point[1] + self.temp_shape.height/2
                        self.temp_shape.y_center = int(value)
                elif self.shape_type == "ellipse":
                    value = int(abs(self.end_point[0] - self.start_point[0]))
                    self.temp_shape.x_axis = value
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.temp_shape.y_axis = self.temp_shape.x_axis
                    else:
                        value = abs(self.end_point[1] - self.start_point[1])
                        self.temp_shape.y_axis = int(value)
                    #Static center
#                    self.temp_shape.x_center = int(self.start_point[0])
#                    self.temp_shape.y_center = int(self.start_point[1])
                    #Moving center
                    if self.start_point[0] < self.end_point[0]:
                        value = self.start_point[0] + self.temp_shape.x_axis
                        self.temp_shape.x_center = int(value)
                    else:
                        value = self.end_point[0] + self.temp_shape.x_axis
                        self.temp_shape.x_center = int(value)
                    if self.start_point[1] < self.end_point[1]:
                        value = self.start_point[1] + self.temp_shape.y_axis
                        self.temp_shape.y_center = int(value)
                    else:
                        value = self.end_point[1] + self.temp_shape.y_axis
                        self.temp_shape.y_center = int(value)
                wid.queue_draw()
                self.temp_shape.draw(wid.window, self.graphic_context)
        elif self.action == "resize":
            if self.resizing_shape_started == False:
                self.resizing_shape = self.selected_shape
                resize = self.resizing_shape
                if isinstance(self.resizing_shape, Rectangle):
                    self.initial_point = (resize.x_center - resize.width/2,
                                          resize.y_center - resize.height/2)
                elif isinstance(self.resizing_shape, Ellipse):
                    self.initial_point = (resize.x_center - resize.x_axis,
                                          resize.y_center - resize.y_axis)
                self.resizing_shape_started = True
            else:
                self.final_point = (event.x, event.y)
                if isinstance(self.resizing_shape, Rectangle):
                    value = abs(self.final_point[0] - self.initial_point[0])
                    self.resizing_shape.width = int(value)
                    resize = self.resizing_shape
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.resizing_shape.height = self.resizing_shape.width
                    else:
                        value = abs(self.final_point[1] - self.initial_point[1])
                        self.resizing_shape.height = int(value)
                    if self.initial_point[0] < self.final_point[0]:
                        value = self.initial_point[0] + resize.width/2
                        self.resizing_shape.x_center = int(value)
                    else:
                        value = self.final_point[0] + resize.width/2
                        self.resizing_shape.x_center = int(value)
                    if self.initial_point[1] < self.final_point[1]:
                        value = self.initial_point[1] + resize.height/2
                        self.resizing_shape.y_center = int(value)
                    else:
                        value = self.final_point[1] + resize.height/2
                        self.resizing_shape.y_center = int(value)
                elif isinstance(self.resizing_shape, Ellipse):
                    resize = self.resizing_shape
                    value = abs(self.end_point[0] - self.start_point[0])
                    self.resizing_shape.x_axis = int(value)
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.resizing_shape.y_axis = self.resizing_shape.x_axis
                    else:
                        value = abs(self.final_point[1] - self.initial_point[1])
                        self.resizing_shape.y_axis = int(value)
                    if self.initial_point[0] < self.final_point[0]:
                        value = self.initial_point[0] + resize.x_axis
                        self.resizing_shape.x_center = int(value)
                    else:
                        value = self.final_point[0] + resize.x_axis
                        self.resizing_shape.x_center = int(value)
                    if self.initial_point[1] < self.final_point[1]:
                        value = self.initial_point[1] + resize.y_axis
                        self.resizing_shape.y_center = int(value)
                    else:
                        value = self.final_point[1] + resize.y_axis
                        self.resizing_shape.y_center = int(value)
                wid.queue_draw()
                self.resizing_shape.draw(wid.window, self.graphic_context)
        elif self.action == "move":
            if self.moving_shape_started == False:
                self.moving_shape = self.selected_shape
                self.first_point = (event.x, event.y)
                self.moving_shape_started = True
            else:
                self.last_point = (event.x, event.y)
                self.moving_shape.x_center = int(self.last_point[0])
                self.moving_shape.y_center = int(self.last_point[1])
                wid.queue_draw()
                self.moving_shape.draw(wid.window, self.graphic_context)

    def finish_shape(self, wid, event, model, area_name, area_desc, treeview):
        ''' Another behemoth function. This complements the compose_shape
            function: what compose start, finish ends. '''

        if self.action == "add":
            if self.composing_shape == True:
                self.end_point = (event.x, event.y)
                if self.shape_type == "rectangle":
                    value = abs(self.end_point[0] - self.start_point[0])
                    self.temp_shape.width = int(value)
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.temp_shape.height = self.temp_shape.width
                    else:
                        value = abs(self.end_point[1] - self.start_point[1])
                        self.temp_shape.height = int(value)
                    if self.start_point[0] < self.end_point[0]:
                        value = self.start_point[0] + self.temp_shape.width/2
                        self.temp_shape.x_center = int(value)
                    else:
                        value = self.end_point[0] + self.temp_shape.width/2 
                        self.temp_shape.x_center = int(value)
                    if self.start_point[1] < self.end_point[1]:
                        value = self.start_point[1] + self.temp_shape.height/2
                        self.temp_shape.y_center = int(value)
                    else:
                        value = self.end_point[1] + self.temp_shape.height/2
                        self.temp_shape.y_center = int(value)
                elif self.shape_type == "ellipse":
                    value = self.end_point[0] - self.start_point[0]
                    self.temp_shape.x_axis = int(abs(value))
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.temp_shape.y_axis = self.temp_shape.x_axis
                    else:
                        value = abs(self.end_point[1] - self.start_point[1])
                        self.temp_shape.y_axis = int(value)
                    if self.start_point[0] < self.end_point[0]:
                        value = self.start_point[0] + self.temp_shape.x_axis
                        self.temp_shape.x_center = int(value)
                    else:
                        value = self.end_point[0] + self.temp_shape.x_axis
                        self.temp_shape.x_center = int(value)
                    if self.start_point[1] < self.end_point[1]:
                        value = self.start_point[1] + self.temp_shape.y_axis
                        self.temp_shape.y_center = int(value)
                    else:
                        value = self.end_point[1] + self.temp_shape.y_axis
                        self.temp_shape.y_center = int(value)
                self.temp_shape.draw(wid.window, self.graphic_context)
                self.composing_shape = False
                #save temp_shape on the areas list
                name = area_name.get_text()
                desc = area_desc.get_text()
                shape_iter = model.append([name, self.temp_shape, desc])
                treeview.set_cursor( model.get_path(shape_iter) )
                self.select_area(treeview, wid, area_name, area_desc)
        elif self.action == "resize":
            if self.resizing_shape_started == True:
                self.final_point = (event.x, event.y)
                if isinstance(self.resizing_shape, Rectangle):
                    value = self.final_point[0] - self.initial_point[0]
                    self.resizing_shape.width = int(abs(value))
                    resize = self.resizing_shape
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.resizing_shape.height = self.resizing_shape.width
                    else:
                        value = self.final_point[1] - self.initial_point[1]
                        self.resizing_shape.height = int(abs(value))
                    if self.initial_point[0] < self.final_point[0]:
                        value = self.initial_point[0] + resize.width/2
                        self.resizing_shape.x_center = int(value)
                    else:
                        value = self.final_point[0] + resize.width/2
                        self.resizing_shape.x_center = int(value)
                    if self.initial_point[1] < self.final_point[1]:
                        value = self.initial_point[1] + resize.height/2
                        self.resizing_shape.y_center = int(value)
                    else:
                        value = self.final_point[1] + resize.height/2
                        self.resizing_shape.y_center = int(value)
                elif isinstance(self.resizing_shape, Ellipse):
                    value = self.end_point[0] - self.start_point[0]
                    self.resizing_shape.x_axis = int(abs(value))
                    resize = self.resizing_shape
                    if event.state & gtk.gdk.BUTTON1_MASK and \
                       event.state & gtk.gdk.SHIFT_MASK:
                        self.resizing_shape.y_axis = self.resizing_shape.x_axis
                    else:
                        value = self.final_point[1] - self.initial_point[1]
                        self.resizing_shape.y_axis = int(abs(value))
                    if self.initial_point[0] < self.final_point[0]:
                        value = self.initial_point[0] + resize.x_axis
                        self.resizing_shape.x_center = int(value)
                    else:
                        value = self.final_point[0] + resize.x_axis
                        self.resizing_shape.x_center = int(value)
                    if self.initial_point[1] < self.final_point[1]:
                        value = self.initial_point[1] + resize.y_axis
                        self.resizing_shape.y_center = int(value)
                    else:
                        value = self.final_point[1] + resize.y_axis
                        self.resizing_shape.y_center = int(value)
                self.resizing_shape.draw(wid.window, self.graphic_context)
                wid.queue_draw()
                self.resizing_shape_started = False
        elif self.action == "move":
            if self.moving_shape_started == True:
                self.last_point = (event.x, event.y)
                self.moving_shape.x_center = int(self.last_point[0])
                self.moving_shape.y_center = int(self.last_point[1])
                self.moving_shape.draw(wid.window, self.graphic_context)
                self.moving_shape_started = False
        wid.queue_draw()

    def draw_expose(self, wid, event, project, areas_list):
        ''' Redraw the areas on top of the image. '''

        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)
        wid.window.draw_pixbuf(self.graphic_context, project.refimage,
                               0, 0, 0, 0,-1,-1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        values = [ r[1] for r in areas_list ]
        for shape in values:
            shape.draw(wid.window, self.graphic_context)
        if self.selected_shape:
            self.selected_shape.draw(wid.window, self.red_gc)

    def remove_area(self, wid):
        ''' Remove an area from the model. '''
        view = self.xml.get_widget("treeviewAreas")
        model, itr = view.get_selection().get_selected()
        if itr:
            model.remove(itr)
        
        widget = self.xml.get_widget("drawingareaAreas")
        widget.emit("expose_event", gtk.gdk.Event(gtk.gdk.NOTHING))
    
    def shape_action(self, wid, action):
        ''' Set the action to be executed. '''
        self.action = action
