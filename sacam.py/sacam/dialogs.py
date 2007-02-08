from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from sacam.areas import ellipse, rectangle, area, line

from sacam.i18n import _

class prop_diag(object):
    
    def run(self, wid, project, xml):
        propdiag = xml.get_widget("dialogProjProp"); 
        propdiag.show_all()
        experiment = project.current_experiment
        
        entryBio = xml.get_widget("entryNameProject")
        entryExp = xml.get_widget("entryNameExperiment")
        entryName = xml.get_widget("entryNameInsect")
        entryComp = xml.get_widget("entryComp")
        entryTemp = xml.get_widget("entryTemp")
        hscaleThreshold = xml.get_widget("hscaleThreshold")
        
        try: t = project.attributes[_("Project Name")]
        except KeyError: entryBio.props.text = ""
        else: entryBio.props.text = t
        
        try: t = experiment.attributes[_("Experiment Name")]
        except KeyError: entryExp.props.text = ""
        else: entryExp.props.text = t
        
        try: t = project.attributes[_("Insect Name")]
        except KeyError: entryName.props.text = ""
        else: entryName.props.text = t
            
        try: t = project.attributes[_("Compounds used")]
        except KeyError: entryComp.props.text = ""
        else: entryComp.props.text = t
        
        try: t = project.attributes[_("Temperature")]
        except KeyError: entryTemp.props.text = ""
        else: entryTemp.props.text = t
            
        hscaleThreshold.set_value(project.current_experiment.threshold)
            
        response = propdiag.run()        
        if response == gtk.RESPONSE_OK :
            project.attributes[_("Project Name")] = entryBio.props.text
            project.attributes[_("Insect Name")] = entryName.props.text
            project.attributes[_("Compounds used")] = entryComp.props.text
            project.attributes[_("Temperature")] = entryTemp.props.text
            experiment.attributes[_("Experiment Name")] = entryExp.props.text                        
            experiment.threshold = hscaleThreshold.get_value()
            propdiag.hide_all()
            window = xml.get_widget("mainwindow")
            window.set_title( ("SACAM - %s - %s") %
                              ( project.attributes[_("Project Name")] ,
                                experiment.attributes[_("Experiment Name")] ) )
            return True
        else:
            propdiag.hide_all()            
            return False
        

class refimg_diag(object):
    
    def __init__(self, xml):
        self.xml = xml
    
    def run(self, wid, project, device, interface):
        widget = self.xml.get_widget('buttonConfirm')
        widget.connect('clicked', self.capture, project, device)
        
        refimg_widget = self.xml.get_widget("imageRefImg")
        if project.refimage:
            refimg_widget.set_from_pixbuf(project.refimage)
        
        refimgDiag = self.xml.get_widget("dialogRefImage");        
        refimgDiag.show_all()        
        response = refimgDiag.run()
                
        if response == gtk.RESPONSE_OK :
            refImg = refimg_widget.get_pixbuf()
            if refImg:
                project.refimage = refImg
            refimgDiag.hide_all()
            interface.update_state()
            return True
        else:
            refimgDiag.hide_all()
            interface.update_state()
            return False

    def capture(self, widget, project, device):
        image = self.xml.get_widget('imageRefImg')
        project.refimage = device.get_current_frame()
        image.set_from_pixbuf(project.refimage)


class areas_diag(object):    
        
    def __init__(self, project, xml):
        self.xml = xml
        self.project = project
        self.output_handler = None        
        
        # widgets to be used
        output = self.xml.get_widget("drawingareaAreas")
        area_name = self.xml.get_widget("entryAreaName")    
        area_desc = self.xml.get_widget("entryAreaDesc")
                
        # setting up the areas treeview
        view = self.xml.get_widget("treeviewAreas")
        
        # model columns: area name, area shape, area description
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING)
        view.set_model(model)
        
        # renderer of the first column
        renderer = gtk.CellRendererText()
        renderer.props.editable = True
        renderer.connect("edited", self.edited_cb, area_name, view.get_model(), 0)
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        view.append_column(column)
        
        # renderer of the second column
        renderer = gtk.CellRendererText()
        renderer.props.editable = True
        renderer.connect("edited", self.edited_cb, area_desc, view.get_model(), 2)
        column = gtk.TreeViewColumn(_("Description"), renderer, text=2)
        view.append_column(column)
        
        # To treat single selection only
        selection = view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        view.connect("cursor_changed", self.select_area, output, area_name, area_desc)
        
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
                                
        output.add_events(  gtk.gdk.BUTTON_PRESS_MASK 
                          | gtk.gdk.BUTTON_RELEASE_MASK
                          | gtk.gdk.BUTTON_MOTION_MASK
                          | gtk.gdk.KEY_PRESS_MASK
                          | gtk.gdk.KEY_RELEASE_MASK   )
        #these three are necessary to draw something in the draw area
        output.connect("button-press-event", self.compose_shape)
        output.connect("motion-notify-event", self.compose_shape)        
        output.connect("button-release-event", self.finish_shape, model, area_name, area_desc, view)
        
    def edited_cb(self, cell, path, new_text, edit_view, model, column):
        model[path][column] = new_text
        edit_view.set_text(new_text)
    
    def run(self, wid, project, interface):
        self.project = project        
        model = self.xml.get_widget("treeviewAreas").get_model()        
        output = self.xml.get_widget("drawingareaAreas")
        if self.output_handler:
            output.disconnect(self.output_handler)
        self.output_handler = output.connect("expose_event", self.draw_expose,
                                             self.project, model)        
        self.window = self.xml.get_widget("dialogAreas"); 
        self.window.show_all()
        
        model.clear()
        for ar in project.current_experiment.areas_list:
            value = (ar.name, ar.shape, ar.description)
            model.append(value)
        
        response = self.window.run()
        if response == gtk.RESPONSE_OK :
            # read the areas from the treemodel and save in the 
            # current experiment areas list
            values = [ (r[0],r[1],r[2]) for r in model ]
            project.current_experiment.areas_list = []
            for name, shape, desc in values:
                project.current_experiment.areas_list.append(area(name, desc, shape))
                
            # set the release_area attribute of the current experiment
            if isinstance(self.release_area, rectangle):
                release = [ int(self.release_area.y_center - self.release_area.height/2),
                         int(self.release_area.x_center - self.release_area.width/2 ),
                         int(self.release_area.y_center + self.release_area.height/2),  
                         int(self.release_area.x_center + self.release_area.width/2 ) ]
                self.project.current_experiment.release_area = release
            elif isinstance(self.release_area, ellipse):
                release = [ int(self.release_area.y_center - self.release_area.y_axis),
                         int(self.release_area.x_center - self.release_area.x_axis ),
                         int(self.release_area.y_center + self.release_area.y_axis),                             
                         int(self.release_area.x_center + self.release_area.x_axis ) ]
                self.project.current_experiment.release_area = release
            
            self.window.hide_all()
            interface.update_state()
            return True
        else:
            self.window.hide_all()
            interface.update_state()            
            return False            
            
    def set_as_release_area(self, wid):
        try:
            self.release_area = self.selected_shape
        except:
            diag = gtk.MessageDialog ( self.window, 
                                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                       gtk.MESSAGE_ERROR, 
                                       gtk.BUTTONS_OK,
                                       _("An area must be selected") )
            diag.run()
            diag.destroy()
            
    def select_area(self, wid, output, area_name, area_desc):
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
        self.shape_type = shape_type
   
    def compose_shape(self, wid, event):
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)        
        if self.action == "add":
            if self.composing_shape == False:
                self.composing_shape = True     
                if self.shape_type == "rectangle":
                    self.temp_shape = rectangle()
                elif self.shape_type == "ellipse":
                    self.temp_shape = ellipse()        
                self.start_point = (event.x, event.y)                
            else:
                self.end_point = (event.x, event.y)
                if self.shape_type == "rectangle":
                    self.temp_shape.width = int(abs(self.end_point[0] - self.start_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.temp_shape.height = self.temp_shape.width
                    else:
                        self.temp_shape.height = int(abs(self.end_point[1] - self.start_point[1]))
                    #Static center
#                    self.temp_shape.x_center = int(self.start_point[0])
#                    self.temp_shape.y_center = int(self.start_point[1])
                    #Moving center                                                            
                    if self.start_point[0] < self.end_point[0]:
                        self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.width/2)
                    else:
                        self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.width/2)           
                    if self.start_point[1] < self.end_point[1]:
                        self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.height/2)
                    else:
                        self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.height/2)
                elif self.shape_type == "ellipse":
                    self.temp_shape.x_axis = int(abs(self.end_point[0] - self.start_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.temp_shape.y_axis = self.temp_shape.x_axis
                    else:                    
                        self.temp_shape.y_axis = int(abs(self.end_point[1] - self.start_point[1]))
                    #Static center
#                    self.temp_shape.x_center = int(self.start_point[0])
#                    self.temp_shape.y_center = int(self.start_point[1])
                    #Moving center                                        
                    if self.start_point[0] < self.end_point[0]:
                        self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.x_axis)
                    else:
                        self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.x_axis)
                    if self.start_point[1] < self.end_point[1]:
                        self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.y_axis)
                    else:
                        self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.y_axis)
                wid.queue_draw()                
                self.temp_shape.draw(wid.window, self.graphic_context)                    
        elif self.action == "resize":
            if self.resizing_shape_started == False:
                self.resizing_shape = self.selected_shape
                if isinstance(self.resizing_shape, rectangle):                
                    self.initial_point = (self.resizing_shape.x_center - self.resizing_shape.width/2,
                                          self.resizing_shape.y_center - self.resizing_shape.height/2)
                elif isinstance(self.resizing_shape, ellipse):
                    self.initial_point = (self.resizing_shape.x_center - self.resizing_shape.x_axis,
                                          self.resizing_shape.y_center - self.resizing_shape.y_axis)
                self.resizing_shape_started = True
            else:
                self.final_point = (event.x, event.y)
                if isinstance(self.resizing_shape, rectangle):
                    self.resizing_shape.width = int(abs(self.final_point[0] - self.initial_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.resizing_shape.height = self.resizing_shape.width
                    else:
                        self.resizing_shape.height = int(abs(self.final_point[1] - self.initial_point[1]))
                    if self.initial_point[0] < self.final_point[0]:
                        self.resizing_shape.x_center = int(self.initial_point[0] + self.resizing_shape.width/2)
                    else:
                        self.resizing_shape.x_center = int(self.final_point[0] + self.resizing_shape.width/2)
                    if self.initial_point[1] < self.final_point[1]:
                        self.resizing_shape.y_center = int(self.initial_point[1] + self.resizing_shape.height/2)
                    else:
                        self.resizing_shape.y_center = int(self.final_point[1] + self.resizing_shape.height/2)
                elif isinstance(self.resizing_shape, ellipse):
                    self.resizing_shape.x_axis = int(abs(self.end_point[0] - self.start_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.resizing_shape.y_axis = self.resizing_shape.x_axis
                    else:                    
                        self.resizing_shape.y_axis = int(abs(self.final_point[1] - self.initial_point[1]))
                    if self.initial_point[0] < self.final_point[0]:
                        self.resizing_shape.x_center = int(self.initial_point[0] + self.resizing_shape.x_axis)
                    else:
                        self.resizing_shape.x_center = int(self.final_point[0] + self.resizing_shape.x_axis)
                    if self.initial_point[1] < self.final_point[1]:
                        self.resizing_shape.y_center = int(self.initial_point[1] + self.resizing_shape.y_axis)
                    else:
                        self.resizing_shape.y_center = int(self.final_point[1] + self.resizing_shape.y_axis)
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
        if self.action == "add":
            if self.composing_shape == True:
                self.end_point = (event.x, event.y)            
                if self.shape_type == "rectangle":
                    self.temp_shape.width = int(abs(self.end_point[0] - self.start_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.temp_shape.height = self.temp_shape.width
                    else:                
                        self.temp_shape.height = int(abs(self.end_point[1] - self.start_point[1]))
                    if self.start_point[0] < self.end_point[0]:
                        self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.width/2)
                    else:
                        self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.width/2)           
                    if self.start_point[1] < self.end_point[1]:
                        self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.height/2)
                    else:
                        self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.height/2)
                elif self.shape_type == "ellipse":
                    self.temp_shape.x_axis = int(abs(self.end_point[0] - self.start_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.temp_shape.y_axis = self.temp_shape.x_axis
                    else:                    
                        self.temp_shape.y_axis = int(abs(self.end_point[1] - self.start_point[1]))
                    if self.start_point[0] < self.end_point[0]:
                        self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.x_axis)
                    else:
                        self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.x_axis)
                    if self.start_point[1] < self.end_point[1]:
                        self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.y_axis)
                    else:
                        self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.y_axis)
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
                if isinstance(self.resizing_shape, rectangle):
                    self.resizing_shape.width = int(abs(self.final_point[0] - self.initial_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.resizing_shape.height = self.resizing_shape.width
                    else:
                        self.resizing_shape.height = int(abs(self.final_point[1] - self.initial_point[1]))
                    if self.initial_point[0] < self.final_point[0]:
                        self.resizing_shape.x_center = int(self.initial_point[0] + self.resizing_shape.width/2)
                    else:
                        self.resizing_shape.x_center = int(self.final_point[0] + self.resizing_shape.width/2)
                    if self.initial_point[1] < self.final_point[1]:
                        self.resizing_shape.y_center = int(self.initial_point[1] + self.resizing_shape.height/2)
                    else:
                        self.resizing_shape.y_center = int(self.final_point[1] + self.resizing_shape.height/2)
                elif isinstance(self.resizing_shape, ellipse):
                    self.resizing_shape.x_axis = int(abs(self.end_point[0] - self.start_point[0]))
                    if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                        self.resizing_shape.y_axis = self.resizing_shape.x_axis
                    else:                    
                        self.resizing_shape.y_axis = int(abs(self.final_point[1] - self.initial_point[1]))
                    if self.initial_point[0] < self.final_point[0]:
                        self.resizing_shape.x_center = int(self.initial_point[0] + self.resizing_shape.x_axis)
                    else:
                        self.resizing_shape.x_center = int(self.final_point[0] + self.resizing_shape.x_axis)
                    if self.initial_point[1] < self.final_point[1]:
                        self.resizing_shape.y_center = int(self.initial_point[1] + self.resizing_shape.y_axis)
                    else:
                        self.resizing_shape.y_center = int(self.final_point[1] + self.resizing_shape.y_axis)
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
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)
        wid.window.draw_pixbuf(self.graphic_context, project.refimage, 
                               0, 0, 0, 0,-1,-1, gtk.gdk.RGB_DITHER_NONE, 0, 0)   
        values = [ r[1] for r in areas_list ]
        for shape in values:
            shape.draw(wid.window, self.graphic_context)
    
    def remove_area(self, wid):
        view = self.xml.get_widget("treeviewAreas")
        model, itr = view.get_selection().get_selected()
        model.remove(itr)
        
        widget = self.xml.get_widget("drawingareaAreas")
        widget.emit("expose_event", gtk.gdk.Event(gtk.gdk.NOTHING))        
    
    def shape_action(self, wid, action):
        self.action = action

class scale_diag(object):
    def __init__(self, xml, project):
        self.xml = xml
        self.project = project
        self.output_handler = None
        
        widget = self.xml.get_widget("buttonCalculateScale")
        widget.connect("clicked", self.calculate_scale)
        
        widget = self.xml.get_widget("comboboxentryUnit")
        widget.connect("changed", self.set_label_unit)
        
        self.graphic_context = None
                                
        entryShapeXSize = self.xml.get_widget("entryShapeXSize")
        entryShapeYSize = self.xml.get_widget("entryShapeYSize")        
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
        
    def run(self, wid, project, interface):
        self.project = project
        output = self.xml.get_widget("drawingareaScale")
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
        if isinstance(self.temp_shape, rectangle):
            x_shape_size = self.temp_shape.width / x_scale_ratio
            y_shape_size = self.temp_shape.height / y_scale_ratio
        elif isinstance(self.temp_shape, ellipse):
            x_shape_size = self.temp_shape.x_axis * 2 / x_scale_ratio
            y_shape_size = self.temp_shape.y_axis * 2 / y_scale_ratio
        elif isinstance(self.temp_shape, line):
            x_shape_size = sqrt( pow(self.temp_shape.x_end - self.temp_shape.x_start, 2)
                           + pow(self.temp_shape.y_end - self.temp_shape.y_start, 2) ) \
                           / x_scale_ratio
            y_shape_size = x_shape_size
        self.xml.get_widget("entryShapeXSize").set_text(str(x_shape_size))
        self.xml.get_widget("entryShapeYSize").set_text(str(y_shape_size))

        scaleDiag = self.xml.get_widget("dialogScale"); 
        scaleDiag.show_all()        
        
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(output.window)
        if self.temp_shape:
            self.temp_shape.draw(output.window, self.graphic_context)            
        
        response = scaleDiag.run()
        
        if response == gtk.RESPONSE_OK :
            try:
                value = self.xml.get_widget("comboboxentryUnit").get_active_text()
            except: 
                pass
            else: 
                self.project.current_experiment.measurement_unit = value
            
            try: 
                self.project.current_experiment.x_scale_ratio = self.x_scale
            except:
                pass
                            
            try:
                self.project.current_experiment.y_scale_ratio = self.y_scale            
            except:
                pass
                        
            self.project.current_experiment.scale_shape = self.temp_shape
                        
            scaleDiag.hide_all()
            interface.update_state()
            return True
        else:
            scaleDiag.hide_all()    
            interface.update_state()        
            return False
        
    def draw_expose(self, wid, event, project):
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)
        wid.window.draw_pixbuf(self.graphic_context, project.refimage, 
                               0, 0, 0, 0,-1,-1, gtk.gdk.RGB_DITHER_NONE, 0, 0)       
        if self.temp_shape:
            self.temp_shape.draw(wid.window, self.graphic_context)

    def compose_shape(self, wid, event):
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)        
        if self.composing_shape == False:
            self.composing_shape = True     
            self.start_point = (event.x, event.y)            
            if self.xml.get_widget("radiobuttonEllipse").get_active():
                self.temp_shape = ellipse()
            elif self.xml.get_widget("radiobuttonRectangle").get_active():
                self.temp_shape = rectangle()
            elif self.xml.get_widget("radiobuttonLine").get_active():
                self.temp_shape = line()
                self.temp_shape.x_start = int(self.start_point[0])
                self.temp_shape.y_start = int(self.start_point[1])                
        else:
            self.end_point = (event.x, event.y)
            if isinstance(self.temp_shape, rectangle):
                self.temp_shape.width = int(abs(self.end_point[0] - self.start_point[0]))
                if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                    self.temp_shape.height = self.temp_shape.width
                else:
                    self.temp_shape.height = int(abs(self.end_point[1] - self.start_point[1]))
                if self.start_point[0] < self.end_point[0]:
                    self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.width/2)
                else:
                    self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.width/2)           
                if self.start_point[1] < self.end_point[1]:
                    self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.height/2)
                else:
                    self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.height/2)
            elif isinstance(self.temp_shape, ellipse):
                self.temp_shape.x_axis = int(abs(self.end_point[0] - self.start_point[0]))
                if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                    self.temp_shape.y_axis = self.temp_shape.x_axis
                else:                    
                    self.temp_shape.y_axis = int(abs(self.end_point[1] - self.start_point[1]))
                if self.start_point[0] < self.end_point[0]:
                    self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.x_axis)
                else:
                    self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.x_axis)
                if self.start_point[1] < self.end_point[1]:
                    self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.y_axis)
                else:
                    self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.y_axis)
            elif isinstance(self.temp_shape, line):
                self.temp_shape.x_end = int(self.end_point[0])                    
                self.temp_shape.y_end = int(self.end_point[1])
            wid.queue_draw()                
            self.temp_shape.draw(wid.window, self.graphic_context)                    

    def finish_shape(self, wid, event):
        if self.composing_shape == True:
            self.end_point = (event.x, event.y)            
            if isinstance(self.temp_shape, rectangle):
                self.temp_shape.width = int(abs(self.end_point[0] - self.start_point[0]))
                if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                    self.temp_shape.height = self.temp_shape.width
                else:                
                    self.temp_shape.height = int(abs(self.end_point[1] - self.start_point[1]))
                if self.start_point[0] < self.end_point[0]:
                    self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.width/2)
                else:
                    self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.width/2)           
                if self.start_point[1] < self.end_point[1]:
                    self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.height/2)
                else:
                    self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.height/2)
            elif isinstance(self.temp_shape, ellipse):
                self.temp_shape.x_axis = int(abs(self.end_point[0] - self.start_point[0]))
                if event.get_state() == (gtk.gdk.SHIFT_MASK | gtk.gdk.BUTTON1_MASK):
                    self.temp_shape.y_axis = self.temp_shape.x_axis
                else:                    
                    self.temp_shape.y_axis = int(abs(self.end_point[1] - self.start_point[1]))
                if self.start_point[0] < self.end_point[0]:
                    self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.x_axis)
                else:
                    self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.x_axis)
                if self.start_point[1] < self.end_point[1]:
                    self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.y_axis)
                else:
                    self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.y_axis)
            elif isinstance(self.temp_shape, line):                    
                self.temp_shape.x_end = int(self.end_point[0])                    
                self.temp_shape.y_end = int(self.end_point[1])
            self.temp_shape.draw(wid.window, self.graphic_context)
            self.composing_shape = False

    def calculate_scale(self, wid):
        invalid_value = False
        
        x_size = self.xml.get_widget("entryShapeXSize").get_text()
        try: x_size = float(x_size)
        except: invalid_value = True
            
        y_size = self.xml.get_widget("entryShapeYSize").get_text()
        try: y_size = float(y_size)
        except: invalid_value = True                
        
        #TODO: verify if a shape was drawn
        
        if invalid_value:
            error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, 
                                      gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                      _("Invalid values"))
            response = error.run()
            if response == gtk.RESPONSE_OK:
                error.destroy()
        else:
            if isinstance(self.temp_shape, rectangle):
                x_shape_size = self.temp_shape.width
                y_shape_size = self.temp_shape.height
            elif isinstance(self.temp_shape, ellipse):
                x_shape_size = self.temp_shape.x_axis * 2
                y_shape_size = self.temp_shape.y_axis * 2
            elif isinstance(self.temp_shape, line):            
                x_shape_size = sqrt( pow(self.temp_shape.x_end - self.temp_shape.x_start, 2)
                             + pow(self.temp_shape.y_end - self.temp_shape.y_start, 2) )
                y_shape_size = x_shape_size
            
            self.x_scale = (x_shape_size) / float(x_size)
            self.y_scale = (y_shape_size) / float(y_size)
            
            self.xml.get_widget("entryXAxis").set_text(str(self.x_scale))
            self.xml.get_widget("entryYAxis").set_text(str(self.y_scale))
                
    def set_label_unit(self, wid):
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
            

class insectsize_diag(object):
    def __init__(self, xml):
        self.xml = xml
    
    def run(self, wid, project, interface):
        self.project = project
        insectSizeDiag = self.xml.get_widget("dialogInsectSize");
        
        value = self.project.current_experiment.measurement_unit
        labelSize = self.xml.get_widget("labelSize");
        labelSize.set_label(value)
        labelSpeed = self.xml.get_widget("labelSpeed");
        labelSpeed.set_label(value + "/s")        
        
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
        
        insectSizeDiag.show_all()
        response = insectSizeDiag.run()
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
                
            insectSizeDiag.hide_all()
            interface.update_state()
            return True
        else:
            insectSizeDiag.hide_all()            
            interface.update_state()
            return False
