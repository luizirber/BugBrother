import gtk
import gobject

from areas import circle

class spam(object):    
    
    def destroy(self,widget):
        gtk.main_quit()

    def main(self):        
        window = gtk.Window()
        window.set_default_size(300, 300)
        
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        
        draw_vbox = gtk.VBox()
        
        self.draw_area = gtk.DrawingArea()
        self.draw_area.add_events(  gtk.gdk.BUTTON_PRESS_MASK 
                                  | gtk.gdk.BUTTON_RELEASE_MASK
                                  | gtk.gdk.BUTTON_MOTION_MASK  )
        self.draw_area.connect("expose_event", self.draw_expose)                                  
        self.draw_area.connect("button-press-event", self.compose_shape)
        self.draw_area.connect("motion-notify-event", self.compose_shape)        
        self.draw_area.connect("button-release-event", self.finish_shape)        
        allocation = gtk.gdk.Rectangle(0,0,100,100)
        self.draw_area.size_allocate( allocation )    

        draw_vbox.add(self.draw_area)#, False, False, 10)    
        hbox.add(draw_vbox)#, False, False, 10)
        vbox.add(hbox)#, False, False, 10)        
        window.add(vbox)
        
        self.graphic_context = None
        self.composing_shape = False
        
        window.connect("destroy", self.destroy)
        window.show_all()
        
        gtk.main()
    
    def compose_shape(self, wid, event):
        if not self.graphic_context:
            self.graphic_context = gtk.gdk.GC(wid.window)        

        if self.composing_shape == False:
            self.composing_shape = True     
            self.temp_shape = circle()
            self.start_point = (event.x, event.y)                
        else:
            self.end_point = (event.x, event.y)
            self.temp_shape.radius = int(abs(self.end_point[0] - self.start_point[0])/2)
            if self.start_point[0] < self.end_point[0]:
                self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.radius)
            else:
                self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.radius)
            if self.start_point[1] < self.end_point[1]:
                self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.radius)
            else:
                self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.radius)             
            self.temp_shape.draw(wid.window, self.graphic_context)
    
    def finish_shape(self, wid, event):
        if self.composing_shape == True:
            self.end_point = (event.x, event.y)            
            self.temp_shape.radius = int(abs(self.end_point[0] - self.start_point[0])/2)
            if self.start_point[0] < self.end_point[0]:
                self.temp_shape.x_center = int(self.start_point[0] + self.temp_shape.radius)
            else:
                self.temp_shape.x_center = int(self.end_point[0] + self.temp_shape.radius)
            if self.start_point[1] < self.end_point[1]:
                self.temp_shape.y_center = int(self.start_point[1] + self.temp_shape.radius)
            else:
                self.temp_shape.y_center = int(self.end_point[1] + self.temp_shape.radius)             
            self.temp_shape.draw(wid.window, self.graphic_context)
            self.composing_shape = False
        wid.queue_draw()                    
    
    def draw_expose(self, wid, event):
        pass
            
if __name__ == "__main__":
    obj = spam()
    obj.main()