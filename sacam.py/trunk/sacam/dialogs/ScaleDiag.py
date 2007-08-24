from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from sacam.areas import Ellipse, Rectangle, Area, Line

from sacam.i18n import _

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
        else:
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Radius of shape:'))
                    
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
        
        self.temp_shape = self.project.current_experiment.scale_shape
        x_shape_size = 0
        if isinstance(self.temp_shape, Ellipse):
            x_shape_size = self.temp_shape.x_axis * 2 / x_scale_ratio
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Radius of shape:'))
        elif isinstance(self.temp_shape, Line):
            sum1 = pow(self.temp_shape.x_end - self.temp_shape.x_start, 2)
            x_shape_size = sum1 / x_scale_ratio
            wid = self.xml.get_widget("labelShapeXSize")
            wid.set_text(_('Lenght of Line:'))

        self.xml.get_widget("entryShapeXSize").set_text(str(x_shape_size))

        scale_diag = self.xml.get_widget("dialogScale");
        scale_diag.show_all()

        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(output.window)
            color = gtk.gdk.color_parse("red")
            self.graphic_context.set_rgb_fg_color(color)
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
            color = gtk.gdk.color_parse("red")
            self.graphic_context.set_rgb_fg_color(color)
        wid.window.draw_pixbuf(self.graphic_context, project.refimage,
                               0, 0, 0, 0,-1,-1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        if self.temp_shape:
            self.temp_shape.draw(wid.window, self.graphic_context)

    def compose_shape(self, wid, event):
        ''' Receive the mouse events and begin the drawing of the shape. '''

        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)
            color = gtk.gdk.color_parse("red")
            self.graphic_context.set_rgb_fg_color(color)
        if self.composing_shape == False:
            self.composing_shape = True
            self.start_point = (event.x, event.y)
            if self.xml.get_widget("radiobuttonCircle").get_active():
                self.temp_shape = Ellipse()
            elif self.xml.get_widget("radiobuttonLine").get_active():
                self.temp_shape = Line()
                self.temp_shape.x_start = int(self.start_point[0])
                self.temp_shape.y_start = int(self.start_point[1])
        else:
            self.end_point = (event.x, event.y)
            if isinstance(self.temp_shape, Ellipse):
                value = self.end_point[0] - self.start_point[0]
                self.temp_shape.x_axis = int(abs(value))
                self.temp_shape.y_axis = self.temp_shape.x_axis
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
            if isinstance(self.temp_shape, Ellipse):
                value = self.end_point[0] - self.start_point[0]
                self.temp_shape.x_axis = int(abs(value))
                self.temp_shape.y_axis = self.temp_shape.x_axis
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
                if isinstance(self.temp_shape, Ellipse):
                    x_shape_size = self.temp_shape.x_axis * 2
                elif isinstance(self.temp_shape, Line):
                    value = self.temp_shape.x_end - self.temp_shape.x_start
                    square_x = pow(value, 2)
                    value = self.temp_shape.y_end - self.temp_shape.y_start
                    square_y = pow(value, 2)
                    x_shape_size = sqrt( square_x + square_y )
                    y_shape_size = x_shape_size
                    y_size = x_size
                
                if x_size <= 0:
                    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                   _("Shape size must be greater than zero"))
                    error.run()
                    error.destroy()
                else:
                    self.x_scale = (x_shape_size) / float(x_size)
                    wid = self.xml.get_widget("entryXAxis")
                    wid.set_text(str(self.x_scale))
                
    def set_label_unit(self, wid):
        ''' Set the metric unit in the labels. '''

        widget = self.xml.get_widget("labelUnitXSize")
        widget.set_label(wid.get_active_text())
        
        widget = self.xml.get_widget("labelUnitXAxis")
        widget.set_label("pixels/" + wid.get_active_text())
