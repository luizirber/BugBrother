''' Contains the dialogs needed to define the projects and experiments. '''

from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from sacam.areas import Ellipse, Rectangle, Area, Line

from sacam.i18n import _

class PropDiag(object):
    ''' This dialog sets the project properties. '''

    def run(self, wid, project, xml):
        ''' Run the specific dialog and save the changes in the project. '''

        propdiag = xml.get_widget("dialogProjProp");
        propdiag.show_all()
        experiment = project.current_experiment

        entry_bio = xml.get_widget("entryNameProject")
        entry_exp = xml.get_widget("entryNameExperiment")
        entry_name = xml.get_widget("entryNameInsect")
        entry_comp = xml.get_widget("entryComp")
        entry_temp = xml.get_widget("entryTemp")
        hscale_threshold = xml.get_widget("hscaleThreshold")

        try:
            temp = project.attributes[_("Project Name")]
        except KeyError:
            entry_bio.props.text = ""
        else:
            entry_bio.props.text = temp

        try:
            temp = experiment.attributes[_("Experiment Name")]
        except KeyError:
            entry_exp.props.text = ""
        else:
            entry_exp.props.text = temp

        try:
            temp = project.attributes[_("Insect Name")]
        except KeyError:
            entry_name.props.text = ""
        else:
            entry_name.props.text = temp

        try:
            temp = project.attributes[_("Compounds used")]
        except KeyError:
            entry_comp.props.text = ""
        else:
            entry_comp.props.text = temp

        try:
            temp = project.attributes[_("Temperature")]
        except KeyError:
            entry_temp.props.text = ""
        else:
            entry_temp.props.text = temp

        hscale_threshold.set_value(project.current_experiment.threshold)

        response = propdiag.run()
        if response == gtk.RESPONSE_OK :
            project.attributes[_("Project Name")] = entry_bio.props.text
            project.attributes[_("Insect Name")] = entry_name.props.text
            project.attributes[_("Compounds used")] = entry_comp.props.text
            project.attributes[_("Temperature")] = entry_temp.props.text
            experiment.attributes[_("Experiment Name")] = entry_exp.props.text
            experiment.threshold = hscale_threshold.get_value()
            propdiag.hide_all()
            window = xml.get_widget("mainwindow")
            window.set_title( ("SACAM - %s - %s") %
                              ( project.attributes[_("Project Name")] ,
                                experiment.attributes[_("Experiment Name")] ) )
            return True
        else:
            propdiag.hide_all()
            return False


class RefimgDiag(object):
    ''' This dialog contains the code to capture a pixbuf and save it as the
        reference image for the project. '''

    def __init__(self, xml):
        self.xml = xml

    def run(self, wid, project, device, interface):
        ''' Run the specific dialog and save the changes in the project. '''

        widget = self.xml.get_widget('buttonConfirm')
        widget.connect('clicked', self.capture, project, device)

        refimg_widget = self.xml.get_widget("imageRefImg")
        if project.refimage:
            refimg_widget.set_from_pixbuf(project.refimage)
        refimg_widget.set_size_request(device.frame['width'],
                                       device.frame['height'])

        refimg_diag = self.xml.get_widget("dialogRefImage");
        refimg_diag.show_all()
        response = refimg_diag.run()

        if response == gtk.RESPONSE_OK :
            refimg = refimg_widget.get_pixbuf()
            if refimg:
                project.refimage = refimg
            refimg_diag.hide_all()
            interface.update_state()
            return True
        else:
            refimg_diag.hide_all()
            interface.update_state()
            return False

    def capture(self, widget, project, device):
        ''' Get the image from the device and show on the screen. '''

        image = self.xml.get_widget('imageRefImg')
        project.refimage = device.get_current_frame()
        image.set_from_pixbuf(project.refimage)


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
            if isinstance(self.release_area, Rectangle):
                y_0 = self.release_area.y_center - self.release_area.height/2
                x_0 = self.release_area.x_center - self.release_area.width/2
                y_1 = self.release_area.y_center + self.release_area.height/2
                x_1 = self.release_area.x_center + self.release_area.width/2
                release = [int(y_0), int(x_0), int(y_1), int(x_1)]
                self.project.current_experiment.release_area = release
            elif isinstance(self.release_area, Ellipse):
                y_0 = int(self.release_area.y_center - self.release_area.y_axis)
                x_0 = int(self.release_area.x_center - self.release_area.x_axis)
                y_1 = int(self.release_area.y_center + self.release_area.y_axis)
                x_1 = int(self.release_area.x_center + self.release_area.x_axis)
                release = [y_0, x_0, y_1, x_1]
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
            self.red_gc = output.window.new_gc(color, color)
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

class ScaleDiag(object):
    ''' Dialog that control the scale of the project. '''

    def __init__(self, xml, project):
        self.xml = xml
        self.project = project
        self.output_handler = None
        
        widget = self.xml.get_widget("buttonCalculateScale")
        widget.connect("clicked", self.calculate_scale)
        
        widget = self.xml.get_widget("comboboxentryUnit")
        widget.connect("changed", self.set_label_unit)
        
        self.graphic_context = None

        self.x_scale = None
        self.y_scale = None
        self.start_point = None
        self.end_point = None
        
        widget = self.xml.get_widget("radiobuttonLine")
        widget.connect("toggled", self.toggled)
       
        widget = self.xml.get_widget("drawingareaScale")
        widget.add_events(  gtk.gdk.BUTTON_PRESS_MASK 
                          | gtk.gdk.BUTTON_RELEASE_MASK
                          | gtk.gdk.BUTTON_MOTION_MASK
                          | gtk.gdk.KEY_PRESS_MASK
                          | gtk.gdk.KEY_RELEASE_MASK   )
        #these are necessary to draw something in the draw area
        widget.connect("button-press-event", self.compose_shape)
        widget.connect("motion-notify-event", self.compose_shape)        
        widget.connect("button-release-event", self.finish_shape)
        self.temp_shape = None
        self.composing_shape = False
        
    def toggled(self, button):
        ''' Callback needed to verify if the current shape is a line,
            because lines only got lenght. '''

        if button.get_active():
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Lenght of Line:'))
            self.xml.get_widget("hboxShapeYSize").props.visible = False
        else:
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Size of shape (X Axis):'))
            self.xml.get_widget("hboxShapeYSize").props.visible = True
                    
    def run(self, wid, project, interface):
        ''' Run the specific dialog and save the changes in the project. '''

        self.project = project
        output = self.xml.get_widget("drawingareaScale")
        output.set_size_request(project.refimage.props.width,
                                project.refimage.props.height)
        if self.output_handler:
            output.disconnect(self.output_handler)
        self.output_handler = output.connect("expose_event", self.draw_expose,
                                              self.project)
        
        value = self.project.current_experiment.measurement_unit
        widget = self.xml.get_widget("comboboxentryUnit")
        widget.prepend_text(value)
        widget.set_active(0)
        
        x_scale_ratio = self.project.current_experiment.x_scale_ratio
        self.xml.get_widget("entryXAxis").set_text(str(x_scale_ratio))
        
        y_scale_ratio = self.project.current_experiment.y_scale_ratio
        self.xml.get_widget("entryYAxis").set_text(str(y_scale_ratio))
        
        self.temp_shape = self.project.current_experiment.scale_shape        
        x_shape_size = 0
        y_shape_size = 0
        if isinstance(self.temp_shape, Rectangle):
            x_shape_size = self.temp_shape.width / x_scale_ratio
            y_shape_size = self.temp_shape.height / y_scale_ratio
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Size of shape (X Axis):'))
            self.xml.get_widget("hboxShapeYSize").props.visible = True
        elif isinstance(self.temp_shape, Ellipse):
            x_shape_size = self.temp_shape.x_axis * 2 / x_scale_ratio
            y_shape_size = self.temp_shape.y_axis * 2 / y_scale_ratio
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Size of shape (X Axis):'))
            self.xml.get_widget("hboxShapeYSize").props.visible = True
        elif isinstance(self.temp_shape, Line):
            sum1 = pow(self.temp_shape.x_end - self.temp_shape.x_start, 2)
            sum2 = pow(self.temp_shape.y_end - self.temp_shape.y_start, 2)
            x_shape_size = sqrt(sum1 + sum2) / x_scale_ratio
            y_shape_size = x_shape_size
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Lenght of Line:'))
            self.xml.get_widget("hboxShapeYSize").props.visible = False
           
        self.xml.get_widget("entryShapeXSize").set_text(str(x_shape_size))
        self.xml.get_widget("entryShapeYSize").set_text(str(y_shape_size))

        scale_diag = self.xml.get_widget("dialogScale"); 
        scale_diag.show_all()        
        
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(output.window)
        if self.temp_shape:
            self.temp_shape.draw(output.window, self.graphic_context) 
        response = scale_diag.run()
        
        if response == gtk.RESPONSE_OK :
            value = self.xml.get_widget("comboboxentryUnit").get_active_text()
            self.project.current_experiment.measurement_unit = value

            if self.x_scale:
                self.project.current_experiment.x_scale_ratio = self.x_scale
            else:
                print 'Warning: No x_scale set'

            if self.y_scale:
                self.project.current_experiment.y_scale_ratio = self.y_scale
            else:
                print 'Warning: No y_scale set'
                        
            self.project.current_experiment.scale_shape = self.temp_shape

            scale_diag.hide_all()
            interface.update_state()
            return True
        else:
            scale_diag.hide_all()    
            interface.update_state()        
            return False
        
    def draw_expose(self, wid, event, project):
        ''' Redraw the image and the current shape. '''

        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)
        wid.window.draw_pixbuf(self.graphic_context, project.refimage, 
                               0, 0, 0, 0,-1,-1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        if self.temp_shape:
            self.temp_shape.draw(wid.window, self.graphic_context)

    def compose_shape(self, wid, event):
        ''' Receive the mouse events and begin the drawing of the shape. '''

        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)        
        if self.composing_shape == False:
            self.composing_shape = True     
            self.start_point = (event.x, event.y)            
            if self.xml.get_widget("radiobuttonEllipse").get_active():
                self.temp_shape = Ellipse()
            elif self.xml.get_widget("radiobuttonRectangle").get_active():
                self.temp_shape = Rectangle()
            elif self.xml.get_widget("radiobuttonLine").get_active():
                self.temp_shape = Line()
                self.temp_shape.x_start = int(self.start_point[0])
                self.temp_shape.y_start = int(self.start_point[1])
        else:
            self.end_point = (event.x, event.y)
            if isinstance(self.temp_shape, Rectangle):
                value = self.end_point[0] - self.start_point[0]
                self.temp_shape.width = int(abs(value))
                if event.state & gtk.gdk.BUTTON1_MASK and \
                    event.state & gtk.gdk.SHIFT_MASK:                    
                    self.temp_shape.height = self.temp_shape.width
                else:
                    value = int(abs(self.end_point[1] - self.start_point[1]))
                    self.temp_shape.height = value
                if self.start_point[0] < self.end_point[0]:
                    value = int(self.start_point[0] + self.temp_shape.width/2)
                    self.temp_shape.x_center = value
                else:
                    value = self.end_point[0] + self.temp_shape.width/2 
                    self.temp_shape.x_center = int(value)
                if self.start_point[1] < self.end_point[1]:
                    value = self.start_point[1] + self.temp_shape.height/2
                    self.temp_shape.y_center = int(value)
                else:
                    value = self.end_point[1] + self.temp_shape.height/2
                    self.temp_shape.y_center = int(value)
            elif isinstance(self.temp_shape, Ellipse):
                value = self.end_point[0] - self.start_point[0]
                self.temp_shape.x_axis = int(abs(value))
                if event.state & gtk.gdk.BUTTON1_MASK and \
                    event.state & gtk.gdk.SHIFT_MASK:                    
                    self.temp_shape.y_axis = self.temp_shape.x_axis
                else:                    
                    value = self.end_point[1] - self.start_point[1]
                    self.temp_shape.y_axis = int(abs(value))
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
            elif isinstance(self.temp_shape, Line):
                self.temp_shape.x_end = int(self.end_point[0])
                self.temp_shape.y_end = int(self.end_point[1])
            wid.queue_draw()                
            self.temp_shape.draw(wid.window, self.graphic_context)

    def finish_shape(self, wid, event):
        ''' Receive the mouse events and finish what the compose_shape 
            function started. '''

        if self.composing_shape == True:
            self.end_point = (event.x, event.y)            
            if isinstance(self.temp_shape, Rectangle):
                value = abs(self.end_point[0] - self.start_point[0])
                self.temp_shape.width = int(value)
                if event.state & gtk.gdk.BUTTON1_MASK and \
                    event.state & gtk.gdk.SHIFT_MASK:
                    self.temp_shape.height = self.temp_shape.width
                else:
                    value = self.end_point[1] - self.start_point[1]
                    self.temp_shape.height = int(abs(value))
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
            elif isinstance(self.temp_shape, Ellipse):
                value = self.end_point[0] - self.start_point[0]
                self.temp_shape.x_axis = int(abs(value))
                if event.state & gtk.gdk.BUTTON1_MASK and \
                    event.state & gtk.gdk.SHIFT_MASK:                    
                    self.temp_shape.y_axis = self.temp_shape.x_axis
                else:
                    value = self.end_point[1] - self.start_point[1]
                    self.temp_shape.y_axis = int(abs(value))
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
            elif isinstance(self.temp_shape, Line):
                self.temp_shape.x_end = int(self.end_point[0])
                self.temp_shape.y_end = int(self.end_point[1])
            self.temp_shape.draw(wid.window, self.graphic_context)
            self.composing_shape = False

    def calculate_scale(self, wid):
        ''' Calculate the scale based on the current values. '''

        invalid_value = False
        
        x_size = self.xml.get_widget("entryShapeXSize").get_text()
        try: 
            x_size = float(x_size)
        except ValueError: 
            invalid_value = True
            
        y_size = self.xml.get_widget("entryShapeYSize").get_text()
        try: 
            y_size = float(y_size)
        except ValueError: 
            invalid_value = True
        
        if not self.temp_shape:
            error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, 
                                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                        _("You need to draw a shape!"))
            error.run()
            error.destroy()
        else:
            if invalid_value:
                error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, 
                                          gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                          _("Invalid values"))
                error.run()
                error.destroy()
            else:
                if isinstance(self.temp_shape, Rectangle):
                    x_shape_size = self.temp_shape.width
                    y_shape_size = self.temp_shape.height
                elif isinstance(self.temp_shape, Ellipse):
                    x_shape_size = self.temp_shape.x_axis * 2
                    y_shape_size = self.temp_shape.y_axis * 2
                elif isinstance(self.temp_shape, Line):
                    value = self.temp_shape.x_end - self.temp_shape.x_start
                    square_x = pow(value, 2)
                    value = self.temp_shape.y_end - self.temp_shape.y_start
                    square_y = pow(value, 2)
                    x_shape_size = sqrt( square_x + square_y )
                    y_shape_size = x_shape_size
                    y_size = x_size
                
                if x_size <= 0 or y_size <= 0:
                    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, 
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                   _("Shape size must be greater than zero"))
                    error.run()
                    error.destroy()
                else:
                    self.x_scale = (x_shape_size) / float(x_size)
                    self.y_scale = (y_shape_size) / float(y_size)
                    wid = self.xml.get_widget("entryXAxis")
                    wid.set_text(str(self.x_scale))
                    wid = self.xml.get_widget("entryYAxis")
                    wid.set_text(str(self.y_scale))
                
    def set_label_unit(self, wid):
        ''' Set the metric unit in the labels. '''

        wlist = []
        wlist.append(self.xml.get_widget("labelUnitXSize"))
        wlist.append(self.xml.get_widget("labelUnitYSize"))
        for widget in wlist:
            widget.set_label(wid.get_active_text())
        
        wlist = []            
        wlist.append(self.xml.get_widget("labelUnitXAxis"))
        wlist.append(self.xml.get_widget("labelUnitYAxis"))
        for widget in wlist:
            widget.set_label("pixels/" + wid.get_active_text())        
            

class InsectsizeDiag(object):
    ''' Dialog that control the insect size and speed, parameters
        needed to make the videoprocessor faster. '''

    def __init__(self, xml):
        self.xml = xml
        self.project = None
    
    def run(self, wid, project, interface):
        ''' Run the specific dialog and save the changes in the project. '''

        self.project = project
        insectsize_diag = self.xml.get_widget("dialogInsectSize");
        
        value = self.project.current_experiment.measurement_unit
        self.xml.get_widget("labelSize").set_label(value)
        self.xml.get_widget("labelSpeed").set_label(value + "/s")        
        
        # Snoop Dogg mode ON
        x_scale = self.project.current_experiment.x_scale_ratio
        y_scale = self.project.current_experiment.y_scale_ratio
        if x_scale > y_scale:
            siz = self.project.bug_size / x_scale
            spee = self.project.bug_max_speed / x_scale
        else:
            siz = self.project.bug_size / y_scale
            spee = self.project.bug_max_speed / x_scale
        self.xml.get_widget("entryInsectSize").set_text(str(siz))
        self.xml.get_widget("entryInsectSpeed").set_text(str(spee))
        #Snoop Dogg mode OFF
        
        insectsize_diag.show_all()
        response = insectsize_diag.run()
        if response == gtk.RESPONSE_OK :
            widget = self.xml.get_widget("entryInsectSize")
            try:
                size = float(widget.props.text)
            except ValueError:
                pass
            else:
                self.project.original_bug_size = size
                x_scale = self.project.current_experiment.x_scale_ratio
                y_scale = self.project.current_experiment.y_scale_ratio
                if x_scale > y_scale:
                    size *= self.project.current_experiment.x_scale_ratio
                else:
                    size *= self.project.current_experiment.y_scale_ratio
                self.project.bug_size = size
            
            widget = self.xml.get_widget("entryInsectSpeed")
            try:
                speed = float(widget.props.text)
            except ValueError:
                pass
            else:
                self.project.original_bug_speed = speed
                x_scale = self.project.current_experiment.x_scale_ratio
                y_scale = self.project.current_experiment.y_scale_ratio
                if x_scale > y_scale:
                    speed *= self.project.current_experiment.x_scale_ratio
                else:
                    speed *= self.project.current_experiment.y_scale_ratio
                self.project.bug_max_speed = speed
                
            insectsize_diag.hide_all()
            interface.update_state()
            return True
        else:
            insectsize_diag.hide_all()            
            interface.update_state()
            return False

