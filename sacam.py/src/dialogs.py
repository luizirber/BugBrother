#!/usr/bin/env python
from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from areas import ellipse, rectangle, area, line

class prop_diag(object):
    
    def run(self, wid, project, xml):
        propdiag = xml.get_widget("dialogProjProp"); 
        propdiag.show_all()
        
        entryBio = xml.get_widget("entryNameBio")
        entryName = xml.get_widget("entryNameInsect")
        entryComp = xml.get_widget("entryComp")
        entryTemp = xml.get_widget("entryTemp")
        hscaleThreshold = xml.get_widget("hscaleThreshold")
        
        try: t = project.attributes["Name of the Project"]
        except KeyError: entryBio.props.text = ""
        else: entryBio.props.text = t
        
        try: t = project.attributes["Name of Insect"]
        except KeyError: entryName.props.text = ""
        else: entryName.props.text = t
            
        try: t = project.attributes["Compounds used"]
        except KeyError: entryComp.props.text = ""
        else: entryComp.props.text = t
        
        try: t = project.attributes["Temperature"]
        except KeyError: entryTemp.props.text = ""
        else: entryTemp.props.text = t
            
        hscaleThreshold.set_value(project.current_experiment.threshold)
            
        response = propdiag.run()        
        if response == gtk.RESPONSE_OK :
            project.attributes["Name of the Project"] = entryBio.props.text
            project.attributes["Name of Insect"] = entryName.props.text
            project.attributes["Compounds used"] = entryComp.props.text
            project.attributes["Temperature"] = entryTemp.props.text
            project.current_experiment.threshold = hscaleThreshold.get_value()
            propdiag.hide_all()
            return True
        else:
            propdiag.hide_all()            
            return False     


class refimg_diag(object):
    
    def __init__(self, xml):
        self.xml = xml
    
    def run(self, wid, project, interface):
        refimgDiag = self.xml.get_widget("dialogRefImage");                 
        refimgDiag.show_all()        
        response = refimgDiag.run()
                
        if response == gtk.RESPONSE_OK :
            refImg = self.xml.get_widget("imageRefImg").get_pixbuf()
            if refImg:
                project.refimage = refImg
                interface.invalid_refimg = False
            else:
                interface.invalid_refimg = True
            refimgDiag.hide_all()
            interface.ready_state()            
            return True
        else:
            refimgDiag.hide_all()
            interface.invalid_refimg = True
            interface.ready_state()            
            return False

    def capture(self, widget, project, device):
        image = self.xml.get_widget('imageRefImg')
        project.refimage = device.get_current_frame()
        image.set_from_pixbuf(project.refimage)


class areas_diag(object):    
        
    def __init__(self, project, xml):
        self.xml = xml
        self.project = project
        # setting up the areas treeview
        view = self.xml.get_widget("treeviewAreas")
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        view.set_model(model)
        renderer = gtk.CellRendererText()
        renderer.props.editable = True
        column = gtk.TreeViewColumn("Area", renderer, text=0)
        view.append_column(column)
        selection = view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        view.connect("cursor_changed", self.select_area)
        
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
                                
        #default shape to be drawn
        self.shape_type = "rectangle"
        
        #default action is to add an area
        self.action = "add"
        self.composing_shape = False
        self.moving_shape_started = False
        self.resizing_shape_started = False
        self.graphic_context = None
                                
        edit = self.xml.get_widget("entryAreaName")
        widget = self.xml.get_widget("drawingareaAreas")
        widget.add_events(  gtk.gdk.BUTTON_PRESS_MASK 
                          | gtk.gdk.BUTTON_RELEASE_MASK
                          | gtk.gdk.BUTTON_MOTION_MASK
                          | gtk.gdk.KEY_PRESS_MASK
                          | gtk.gdk.KEY_RELEASE_MASK   )
        #what to do when the draw area is exposed        
        widget.connect("expose_event", self.draw_expose, self.project, model)
        #these two are necessary to draw something in the draw area
        widget.connect("button-press-event", self.compose_shape)
        widget.connect("motion-notify-event", self.compose_shape)        
        widget.connect("button-release-event", self.finish_shape, model, edit, view)
            
    def run(self, wid, project, interface):
        self.project = project
        areasDiag = self.xml.get_widget("dialogAreas"); 
        areasDiag.show_all()        
        response = areasDiag.run()
        if response == gtk.RESPONSE_OK :
            model = self.xml.get_widget("treeviewAreas").get_model()
            values = [ (r[0],r[1]) for r in model ]
            project.current_experiment.areas_list = []
            for name, shape in values:
                project.current_experiment.areas_list.append(area(name, shape))
            areasDiag.hide_all()
            interface.invalid_areas = False            
            interface.ready_state()            
            return True
        else:
            areasDiag.hide_all()
            if project.current_experiment.areas_list == []:
                interface.invalid_areas = True
            interface.ready_state()                
            return False            
            
    def set_as_release_area(self, wid):
        release = self.selected_shape
        if isinstance(release, rectangle):
            release_area = [ int(release.y_center - release.height/2),
                             int(release.x_center - release.width/2 ),
                             int(release.y_center + release.height/2),                             
                             int(release.x_center + release.width/2 ) ]
            self.project.current_experiment.release_area = release_area
        elif isinstance(release, ellipse):
            release_area = [ int(release.y_center - release.y_axis),
                             int(release.x_center - release.x_axis ),
                             int(release.y_center + release.y_axis),                             
                             int(release.x_center + release.x_axis ) ]
            self.project.current_experiment.release_area = release_area
            
    def select_area(self, wid):
        selection = wid.get_selection()
        treemodel, treeiter = selection.get_selected()
        self.selected_shape = treemodel.get_value(treeiter, 1)
   
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
    
    def finish_shape(self, wid, event, model, area_name, treeview):
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
                shape_iter = model.append([name, self.temp_shape])
                treeview.set_cursor( model.get_path(shape_iter) )
                self.select_area(treeview)
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
        model, iter = view.get_selection().get_selected()
        model.remove(iter)
        
        widget = self.xml.get_widget("drawingareaAreas")
        widget.emit("expose_event", gtk.gdk.Event(gtk.gdk.NOTHING))        
    
    def shape_action(self, wid, action):
        self.action = action

class scale_diag(object):
    def __init__(self, xml, project):
        self.xml = xml
        self.project = project
        
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
        #what to do when the draw area is exposed        
        widget.connect("expose_event", self.draw_expose, self.project)
        #these two are necessary to draw something in the draw area
        widget.connect("button-press-event", self.compose_shape)
        widget.connect("motion-notify-event", self.compose_shape)        
        widget.connect("button-release-event", self.finish_shape)
        self.temp_shape = None
        self.composing_shape = False
        
    def run(self, wid, project, interface):
        self.project = project
        scaleDiag = self.xml.get_widget("dialogScale"); 
        scaleDiag.show_all()        
        #connect the callbacks for the scale dialog        
        response = scaleDiag.run()
        
        if response == gtk.RESPONSE_OK :
            interface.invalid_scale = False            
            try:
                value = self.xml.get_widget("comboboxentryUnit").get_active_text()
            except: 
                interface.invalid_scale = True
            else: 
                self.project.current_experiment.measurement_unit = value
            
            try: 
                self.project.current_experiment.x_scale_ratio = self.x_scale
            except:
                interface.invalid_scale = True
                            
            try:
                self.project.current_experiment.y_scale_ratio = self.y_scale            
            except:
                interface.invalid_scale = True
            
            scaleDiag.hide_all()
            interface.ready_state()            
            return True
        else:
            scaleDiag.hide_all()            
            interface.invalid_scale = True
            interface.ready_state()            
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
        
        if invalid_value:
            error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, 
                                      gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                      "Invalid values")
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
        
        insectSizeDiag.show_all()
        response = insectSizeDiag.run()
        if response == gtk.RESPONSE_OK :
            interface.invalid_size = False
            interface.invalid_speed = False
            widget = self.xml.get_widget("entryInsectSize")
            try:
                size = float(widget.props.text)
            except ValueError:
                interface.invalid_size = True
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
                interface.invalid_speed = True
            else:
                self.project.original_bug_speed = speed
                x_scale = self.project.current_experiment.x_scale_ratio
                y_scale = self.project.current_experiment.y_scale_ratio
                if x_scale > y_scale:
                    speed *= self.project.current_experiment.x_scale_ratio
                else:
                    speed *= self.project.current_experiment.y_scale_ratio
                self.project.bug_max_velocity = speed
                
            insectSizeDiag.hide_all()
            interface.ready_state()            
            return True
        else:
            insectSizeDiag.hide_all()            
            interface.invalid_size = True
            interface.ready_state()            
            return False
