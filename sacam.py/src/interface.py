#!/usr/bin/env python

import sys
from os import makedirs

import gc
from datetime import datetime

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
gobject.threads_init()

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
        gladefile = "interface/sacam.glade"
        windowname = "mainwindow"
        
        self.xml = gtk.glade.XML(gladefile)
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
        
        self.window.connect("destroy", self.destroy)
        self.window.show()
        
        return
   
    def main(self):
        gtk.main()

    def save_project(self, widget):
        if self.invalid_path:
            #handle this
            pass
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
                                
        self.invalid_path = True
        
        while self.invalid_path:
            response = fsdialog.run()                        
            if response == gtk.RESPONSE_OK :
                current = fsdialog.get_current_folder()     
                filepath = fsdialog.get_filename()
                filename = filepath[len(current) + 1:]
                try:
                    makedirs(filepath)
                except OSError, why:
                    errordiag = gtk.MessageDialog ( fsdialog, 
                                                    gtk.DIALOG_DESTROY_WITH_PARENT, 
                                                    gtk.MESSAGE_ERROR, 
                                                    gtk.BUTTONS_OK,
                                                    why.args[1] )
                    errordiag.run()
                    errordiag.destroy()                                        
                else:                    
                    self.invalid_path = False
                    fsdialog.destroy()                                        
            else:                
                self.invalid_path = True                 
                fsdialog.destroy()
                return
        
        self.project.name = filename
        self.project.filename = filepath + '/' + filename + '.exp'
        
        propdiag = self.xml.get_widget("windowExpProperties"); 
        response = propdiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the properties            
            propdiag.hide_all()
                
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)        
        self.device_manager.sink.set_xwindow_id(self.device_manager.outputarea.window.xid)                 
                
        refimgDiag = self.xml.get_widget("dialogRefImage"); 
        #connect the callbacks for the refimg dialog        
        response = refimgDiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the refimage
            refimgDiag.hide_all()        
        else:
            self.invalid_refimage = True
        
        areasDiag = self.xml.get_widget("dialogAreas"); 
        #connect the callbacks for the areas dialog        
        response = areasDiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the refimage
            areasDiag.hide_all()
        else:
            self.invalid_areas = True

        scaleDiag = self.xml.get_widget("dialogScale"); 
        #connect the callbacks for the scale dialog        
        response = scaleDiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the scale
            scaleDiag.hide_all()
        
        insectSizeDiag = self.xml.get_widget("dialogAreas"); 
        #connect the callbacks for the insect size dialog        
        response = insectSizeDiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the insect size
            insectSizeDiag.hide_all()
        else:
            self.invalid_size = True
        
                
        self.ready_state()
                
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
                    
        self.ready_state()
        
    def start_video(self, widget, project):
        notebook = self.xml.get_widget("mainNotebook")
        notebook.set_current_page(1)
        
        self.capturing_state()
        
        if self.device_manager.pipeline_capture.get_state() != gst.STATE_PLAYING:
            self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)
        
#        if ( widget.get_active() ):        
#            self.device_manager.start_video(widget, project)
#        else:
#            gobject.source_remove(self.device_manager.timeout_id)
            
        self.running = widget.get_active()
        while self.running:            
            self.device_manager.start_video(widget, project)
            gc.collect()
        
        self.ready_state()

    def capturing_state(self):
        widget = self.xml.get_widget("buttonStart")
        widget.set_sensitive(True)        
       
        widget = self.xml.get_widget("buttonNew")
        widget.set_sensitive(False)        

        widget = self.xml.get_widget("buttonOpen")
        widget.set_sensitive(False)        

        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(False)        

        widget = self.xml.get_widget("buttonManager")
        widget.set_sensitive(False)
        
        widget = self.xml.get_widget("buttonScale")
        widget.set_sensitive(False)
        
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(False)        
        
        widget = self.xml.get_widget("buttonInsectSize")
        widget.set_sensitive(False)                
      
        widget = self.xml.get_widget("buttonTortuosity")
        widget.set_sensitive(False)        
        
        widget = self.xml.get_widget("buttonReport")
        widget.set_sensitive(False)        
            
        widget = self.xml.get_widget("buttonPrint")
        widget.set_sensitive(False)
        
        widget = self.xml.get_widget("buttonProcess")
        widget.set_sensitive(False)                        
        
        widget = self.xml.get_widget("toggleTimer")
        widget.set_sensitive(False)     
                           
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(False)    
    
    def ready_state(self):        
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)        
        self.device_manager.sink.set_xwindow_id(self.device_manager.outputarea.window.xid)                
        
        widget = self.xml.get_widget("buttonNew")
        widget.set_sensitive(True)        

        widget = self.xml.get_widget("buttonOpen")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonStart")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonManager")
        widget.set_sensitive(True)
        
        widget = self.xml.get_widget("buttonScale")
        widget.set_sensitive(True)
        
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonInsectSize")
        widget.set_sensitive(True)                
      
        if len(self.project.current_experiment.point_list) == 0 or \
           len(self.project.current_experiment.areas_list) == 0:
            pass
        else:
            widget = self.xml.get_widget("buttonTortuosity")
            widget.set_sensitive(True)        
        
            widget = self.xml.get_widget("buttonReport")
            widget.set_sensitive(True)        
            
            widget = self.xml.get_widget("buttonPrint")
            widget.set_sensitive(True)
            
            if not self.invalid_refimage:
                widget = self.xml.get_widget("buttonProcess")
                widget.set_sensitive(True)
            
        if self.invalid_size or self.invalid_areas:
            pass
        else:
            pass
       
        widget = self.xml.get_widget("toggleTimer")
        widget.set_sensitive(True)     
                           
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(True)    
        
if __name__ == "__main__":
    base = Interface()
    base.main()
