import gtk
import gobject

from videoprocessor import Videoprocessor

class spam(object):

    def __init__(self):
        self.running = False
        self.video = Videoprocessor()
        self.video.previous = gtk.gdk.pixbuf_new_from_file("bitmap/1.bmp")
        self.video.current = gtk.gdk.pixbuf_new_from_file("bitmap/2.bmp")
        
        self.video.startTimer()

    def destroy(self,widget):
        gtk.main_quit()
        
    def run(self, widget):
        if self.running:
            gobject.source_remove(self.timeout_id)
            self.running = False
        else:
            self.timeout_id = gobject.timeout_add(100, self.repeat, widget)
            self.running = True

    def repeat(self, widget):        
        temp = self.video.previous
        self.video.previous = self.video.current
        self.video.current = temp
        
        while gtk.events_pending():
            gtk.main_iteration()

        self.current_view.window.draw_pixbuf(None, self.video.current, 0, 0, 0, 0)
        self.previous_view.window.draw_pixbuf(None, self.video.previous, 0, 0, 0, 0)
        
        return True
    
    def main(self):        
        window = gtk.Window()
        window.set_default_size(300, 300)
        
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        
        current_vbox = gtk.VBox()
        previous_vbox = gtk.VBox()
        
        self.current_view, self.previous_view = gtk.DrawingArea(), gtk.DrawingArea()
        allocation = gtk.gdk.Rectangle(0,0,100,100)
        self.current_view.size_allocate( allocation )
        self.previous_view.size_allocate( allocation )    
        
        current_label, previous_label = gtk.Label("current: "), gtk.Label("previous: ")
        button = gtk.Button("Start")
        button.connect("clicked", self.run)
    
        current_vbox.add(current_label)#, False, False, 10)
        current_vbox.add(self.current_view)#, False, False, 10)
        
        previous_vbox.add(previous_label)#, False, False, 10)
        previous_vbox.add(self.previous_view)#, False, False, 10)    
        
        hbox.add(current_vbox)#, False, False, 10)
        hbox.add(previous_vbox)#, False, False, 10)
        
        vbox.add(hbox)#, False, False, 10)
        vbox.add(button)#, False, False, 10)
        
        window.add(vbox)
        
        window.connect("destroy", self.destroy)
        window.show_all()
        
        gtk.main()
    
if __name__ == "__main__":
    obj = spam()
    obj.main()