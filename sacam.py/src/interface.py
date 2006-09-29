#!/usr/bin/env python

import sys
from os import mkdir, makedirs

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import pygst
pygst.require('0.10')
import gst

from device_manager import Device_manager
from project import project

class Interface(object):
    
    device_manager = None
    window = None
    xml = None
    image = None
    project = None
    
    def __init__(self):
        gladefile = "sacam.glade"
        windowname = "mainwindow"
        
        self.xml = gtk.glade.XML(gladefile, windowname)
        self.window = self.xml.get_widget(windowname)
        self.project = project()
        
        outputarea = self.xml.get_widget("videoOutputArea")
        proc_output = self.xml.get_widget("trackArea")
        self.device_manager = Device_manager(outputarea, proc_output)
        
        widget = self.xml.get_widget("buttonManager")
        widget.connect("toggled", self.manager_toggled)
        
        widget = self.xml.get_widget("buttonNew")
        widget.connect("clicked", self.new_project)
        
        widget = self.xml.get_widget("buttonStart")
        widget.connect("clicked", self.start_video, 
                                  self.project)
        
        widget = self.xml.get_widget("buttonPreferences")
        widget.connect("clicked", self.device_manager.show_window)
        
        widget = self.xml.get_widget("buttonSave")
        widget.connect("clicked", self.save_project)
        
        widget = self.xml.get_widget("buttonOpen")
        widget.connect("clicked", self.load_project)
        
        widget = self.xml.get_widget("buttonStart")
        widget.set_sensitive(True)
        
        self.window.connect("destroy", self.destroy)
        self.window.show()
        
        return
   
    def main(self):
        gtk.main()

    def save_project(self, widget):
        self.project.save_project()

    def destroy(self, widget):
        gtk.main_quit()
     
    def manager_toggled(self, widget):
        b = gtk.ToggleButton.get_active(widget)
        widget = self.xml.get_widget("frameExpManager")
        if b==True:
            widget.show()
        else:
            widget.hide()
            
    def new_project(self, widget):
        main = self.xml.get_widget("mainwindow")
        fsdialog = gtk.FileChooserDialog("Save Project", main,
                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT |
                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OK, gtk.RESPONSE_OK) )
                
        response = fsdialog.run()
        
        if ( response != gtk.RESPONSE_OK ):
            fsdialog.destroy()        
        else:
            filepath = fsdialog.get_current_folder()
            filename = fsdialog.get_filename()[len(filepath) + 1:]
            try:
                makedirs(filepath)
            except:
                pass
        fsdialog.destroy()
        
        self.project.name = filename
        self.project.filename = filepath + '/' + filename + '/' + filename + '.exp'
        
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(True)                        
        
    def load_project(self, widget):
        main = self.xml.get_widget("mainwindow")
        fsdial = gtk.FileChooserDialog("Load Project", main,
                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT |
                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OK, gtk.RESPONSE_OK) )
                
        response = fsdial.run()
        
        if ( response != gtk.RESPONSE_OK ):
            fsdial.destroy()
        else:
            filepath = fsdial.get_current_folder()
            filename = fsdial.get_filename()[len(filepath) + 1:]
            self.project.filename = filepath + '/' + filename + '/' + filename + '.exp'
        fsdial.destroy()
        
        if self.project.filename:
            self.project.load_project()
        
        # this can be made in a better way        
        widget = self.xml.get_widget("buttonManager")
        widget.set_sensitive(True)
        
        widget = self.xml.get_widget("buttonPrint")
        widget.set_sensitive(True)
        
        widget = self.xml.get_widget("buttonTortuosity")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonReport")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonScale")
        widget.set_sensitive(True)
        
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonInsectSize")
        widget.set_sensitive(True)                
        
        widget = self.xml.get_widget("buttonProcess")
        widget.set_sensitive(True)                        
        
        widget = self.xml.get_widget("buttonStart")
        widget.set_sensitive(True)                        
        
        widget = self.xml.get_widget("buttonTrackSimulator")
        widget.set_sensitive(True)                        
        
        widget = self.xml.get_widget("toggleTimer")
        widget.set_sensitive(True)                        
        
    def start_video(self, widget, experiment):
#        widget = self.xml.get_widget("hboxVideoOutput")        
#        widget.add(self.device_manager.foreignGtk)                
        self.device_manager.start_video(widget, experiment)
        
if __name__ == "__main__":
    base = Interface()
    base.main()
