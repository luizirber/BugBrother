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
    invalid_size = False
    invalid_areas = False
    invalid_scale = False
    
    def __init__(self):
        gladefile = "interface/sacam.glade"
        windowname = "mainwindow"
        
        self.xml = gtk.glade.XML(gladefile)
        self.window = self.xml.get_widget(windowname)
        self.project = project()
        
        outputarea = self.xml.get_widget("videoOutputArea")
        proc_output = self.xml.get_widget("trackArea")
        self.device_manager = Device_manager(outputarea, proc_output)
        
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
        
        widget = self.xml.get_widget('buttonConfirm')
        widget.connect('clicked', self.refimgCapture)
        
        return
   
    def run_prop_diag(self):
        propdiag = self.xml.get_widget("dialogProjProp"); 
        response = propdiag.run()
        
        if response == gtk.RESPONSE_OK :
            widget = self.xml.get_widget("entryNameBio")
            self.project.attributes["Name of the Project"] = widget.props.text
            
            widget = self.xml.get_widget("entryNameInsect")
            self.project.attributes["Name of Insect"] = widget.props.text
            
            widget = self.xml.get_widget("entryComp")
            self.project.attributes["Compounds used"] = widget.props.text
                                    
            widget = self.xml.get_widget("entryTemp")
            self.project.attributes["Temperature"] = widget.props.text
            
            propdiag.hide_all()
            return True
        else:
            return False
     
    def run_refimg_diag(self):
        refimgDiag = self.xml.get_widget("dialogRefImage");                 
        response = refimgDiag.run()
                
        if response == gtk.RESPONSE_OK :
            refimgDiag.hide_all()
            return True
        else:
            self.invalid_refimage = True
            return False
        
    def run_areas_diag(self):
        areasDiag = self.xml.get_widget("dialogAreas"); 
        #connect the callbacks for the areas dialog        
        response = areasDiag.run()
        
        if response == gtk.RESPONSE_OK :
            areasDiag.hide_all()
            return True
        else:
            self.invalid_areas = True
            return False
        
    def run_scale_diag(self):
        scaleDiag = self.xml.get_widget("dialogScale"); 
        #connect the callbacks for the scale dialog        
        response = scaleDiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the scale
            scaleDiag.hide_all()
            return True
        else:
            self.invalid_scale = True
            return False
        
    def run_insect_size_diag(self):
        insectSizeDiag = self.xml.get_widget("dialogInsectSize"); 
        #connect the callbacks for the insect size dialog        
        response = insectSizeDiag.run()
        
        if response == gtk.RESPONSE_OK :
#            widget = self.xml.get_widget("entryInsectSize")
#            try:
#                size = float(widget.props.text)
#            except ValueError:
#                self.invalid_size = True
#            else:
#                self.project.bug_size = size
#            
#            widget = self.xml.get_widget("entryInsectSpeed")
#            try:
#                speed = float(widget.props.text)
#            except ValueError:
#                self.invalid_speed = True
#            else:
#                self.project.bug_max_velocity = speed           
            insectSizeDiag.hide_all()
            return True
        else:
            self.invalid_size = True
            return False
                
    
    def main(self):
        gtk.main()

    def save_project(self, widget):
        if self.invalid_path:
            #handle this
            pass
        self.project.save_project()

    def destroy(self, widget):
        gtk.main_quit()
     
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
        
        response = self.run_prop_diag()
        
        if response == False :
            self.ready_state()            
            return
               
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)      
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)
       
        self.device_manager.sink.set_xwindow_id(
                                    self.device_manager.outputarea.window.xid)
                
        response = self.run_refimg_diag()
        if response == False :
            self.ready_state()            
            return
        
        response = self.run_areas_diag()
        if response == False :
            self.ready_state()            
            return

        response = self.run_scale_diag()
        if response == False :
            self.ready_state()
            return
                
        response = self.run_insect_size_diag()
        if response == False :
            self.ready_state()            
            return
                
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
        
    def refimgCapture(self, widget):
        image = self.xml.get_widget('imageRefImg')
        self.project.refimage = self.device_manager.get_current_frame()
        image.set_from_pixbuf(self.project.refimage)
        
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
        if self.running:
            while self.running:            
                self.device_manager.start_video(widget, project)
                gc.collect()
        else:
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

        widget = self.xml.get_widget("buttonScale")
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
        
        widget = self.xml.get_widget("buttonAreas")
        widget.set_sensitive(False)         
        
        widget = self.xml.get_widget("buttonProjProperties")
        widget.set_sensitive(False)         
                           
    def ready_state(self):        
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)        
        self.device_manager.sink.set_xwindow_id(self.device_manager.outputarea.window.xid)                
        
        widget = self.xml.get_widget("buttonNew")
        widget.set_sensitive(True)        

        widget = self.xml.get_widget("buttonOpen")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonSave")
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
            
        widget = self.xml.get_widget("buttonInsectSize")        
        widget.set_sensitive(True)
        
        widget = self.xml.get_widget("buttonScale")        
        widget.set_sensitive(True)
            
        widget = self.xml.get_widget("buttonAreas")
        widget.set_sensitive(True)         
        
        widget = self.xml.get_widget("buttonProjProperties")
        widget.set_sensitive(True)         
            
        widget = self.xml.get_widget("buttonStart")
        if self.invalid_size or self.invalid_areas or \
           self.invalid_scale:
            widget.set_sensitive(False)
        else:
            widget.set_sensitive(True)        
       
        widget = self.xml.get_widget("toggleTimer")
        widget.set_sensitive(True)     
        
if __name__ == "__main__":
    base = Interface()
    base.main()
