#!/usr/bin/env python

import os
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

from kiwi.environ import environ
from sacam.i18n import _, APP_NAME

from sacam.device_manager import Device_manager
from sacam.project import project
from sacam.dialogs import prop_diag, refimg_diag, areas_diag, scale_diag, insectsize_diag

class Interface(object):
        
    def __init__(self):
                
        gladefile = environ.find_resource('glade', 'sacam.glade')
        windowname = "mainwindow"
        
        self.xml = gtk.glade.XML(gladefile, domain=APP_NAME)
        self.window = self.xml.get_widget(windowname)
        
        self.project = project()
        
        outputarea = self.xml.get_widget("videoOutputArea")
        proc_output = self.xml.get_widget("trackArea")
        self.device_manager = Device_manager(outputarea, proc_output)
        self.propdiag = prop_diag()
        self.refimgdiag = refimg_diag(self.xml)
        self.areasdiag = areas_diag(self.project, self.xml)
        self.scalediag = scale_diag(self.xml, self.project)
        self.insectsizediag = insectsize_diag(self.xml)
        
        widget = self.xml.get_widget("buttonNew")
        widget.connect("clicked", self.new_project)
        
        widget = self.xml.get_widget("buttonStart")
        widget.connect("clicked", self.start_video, self.project)
        
        widget = self.xml.get_widget("buttonPreferences")
        widget.connect("clicked", self.device_manager.show_window)
        
        widget = self.xml.get_widget("buttonSave")
        widget.connect("clicked", self.save_project)
        
        widget = self.xml.get_widget("buttonOpen")
        widget.connect("clicked", self.load_project)
        
        widget = self.xml.get_widget("buttonProjProperties")
        widget.connect("clicked", self.propdiag.run, self.project, self.xml)
                            
        widget = self.xml.get_widget("buttonScale")
        widget.connect("clicked", self.scalediag.run, self.project, self)
        
        widget = self.xml.get_widget("buttonInsectSize")
        widget.connect("clicked", self.insectsizediag.run, self.project, self)
                
        widget = self.xml.get_widget("buttonRefImg")
        widget.connect("clicked", self.refimgdiag.run, self.project, self)
        
        widget = self.xml.get_widget("buttonProcess")
        widget.connect("clicked", self.process_lists)        
        
        widget = self.xml.get_widget("buttonReport")
        widget.connect("clicked", self.report)        
                               
        widget = self.xml.get_widget("buttonAreas")
        widget.connect("clicked", self.areasdiag.run, self.project, self)
                                        
        #refimg dialog callback
        widget = self.xml.get_widget('buttonConfirm')
        widget.connect('clicked', self.refimgdiag.capture, self.project, self.device_manager)
        
        #the "invalid_*" variables
        self.invalid_size = True
        self.invalid_areas = True
        self.invalid_scale = True
        self.invalid_refimg = True
        self.invalid_speed = True
        self.invalid_path = True
        
        #home dir
        home = os.curdir
        if 'HOME' in os.environ:
            home = os.environ['HOME']
        elif os.name == 'posix':
            home = os.path.expanduser("~/")
        elif os.name == 'nt':
            if 'HOMEPATH' in os.environ:
                if 'HOMEDRIVE' in os.environ:
                    home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
                else:
                    home = os.environ['HOMEPATH']
        self.home = os.path.realpath(home) + os.sep        
        
        self.window.connect("destroy", self.destroy)
        self.window.set_title( ("SACAM - %s - %s") % 
                               ( self.project.attributes[_("Project Name")],
                                 self.project.current_experiment.attributes[_("Experiment Name")] ) )
        self.window.show()        
        
        self.ready_state()        
        
        return
                 
    def process_lists(self, wid):
        self.project.current_experiment.prepare_point_list()
        self.project.current_experiment.prepare_areas_list()
        self.project.current_experiment.prepare_stats()
               
    def save_project(self, widget):
        if self.invalid_path:
            fsdialog = gtk.FileChooserDialog(_("Save Project"), self.window,
                         gtk.FILE_CHOOSER_ACTION_SAVE,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                         gtk.STOCK_OK, gtk.RESPONSE_OK) )        
            fsdialog.set_current_folder(self.home)
            
            self.invalid_path = True
            while self.invalid_path:
                response = fsdialog.run()                        
                if response == gtk.RESPONSE_OK :
                    current = fsdialog.get_current_folder()     
                    filepath = fsdialog.get_filename()
                    filename = filepath[len(current) + 1:]
                    try:
                        os.makedirs(filepath)
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
            
            self.project.filename = filepath + '/' + filename + '.exp'
            self.project.save()
        else:
            self.project.save()

    def destroy(self, widget):
        self.device_manager.pipeline_capture.set_state(gst.STATE_NULL)                    
        self.device_manager.pipeline_play.set_state(gst.STATE_NULL)
        gtk.main_quit()
     
    def new_project(self, widget):
        if self.project:
            diag = gtk.MessageDialog ( self.window, 
                                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                       gtk.MESSAGE_QUESTION, 
                                       gtk.BUTTONS_YES_NO,
                                       _("Do you want to save the current project?") )
            response = diag.run()
            
            if response == gtk.RESPONSE_YES:
                diag.destroy()                
                self.save_project(None)
                self.project = project()
            else:
                diag.destroy()                
                self.project = project()
        
        response = self.propdiag.run(None, self.project, self.xml)
        
        if response == False :
            self.ready_state()            
            return
               
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)               
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)      
                
        response = self.refimgdiag.run(None, self.project, self)
        if response == False :
            self.ready_state()            
            return
        
        response = self.areasdiag.run(None, self.project, self)
        if response == False :
            self.ready_state()            
            return

        response = self.scalediag.run(None, self.project, self)
        if response == False :
            self.ready_state()
            return
                
        response = self.insectsizediag.run(None, self.project, self)
        if response == False :
            self.ready_state()            
            return
                
        self.ready_state()
                
    def load_project(self, widget):
        main = self.xml.get_widget("mainwindow")
        filename = None
        fsdial = gtk.FileChooserDialog(_("Load Project"), main,
                        gtk.FILE_CHOOSER_ACTION_OPEN,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OK, gtk.RESPONSE_OK) )
        fsdial.set_current_folder(self.home)
                
        response = fsdial.run()
        
        if response != gtk.RESPONSE_OK:
            fsdial.destroy()
        else:
            filename = fsdial.get_filename()
            self.ready_state()            
        fsdial.destroy()
        
        if filename:
            prj = self.project.load(filename)
            if prj:
                self.project = prj
                #TODO: verify the invalid_* values
            else:
                #TODO: print error
                pass
               
    def start_video(self, widget, project):
        notebook = self.xml.get_widget("mainNotebook")
        notebook.set_current_page(1)
        
        x, y = self.device_manager.outputarea.window.get_position()
        self.device_manager.outputarea.size_allocate( gtk.gdk.Rectangle(x, y, 
                                                      self.device_manager.frame_width,
                                                      self.device_manager.frame_height) )
        
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
                
                widget = self.xml.get_widget("labelTime")
                now = datetime(1,1,1).now()
                time = now - project.current_experiment.start_time
                widget.set_text(str(time))
                
                widget = self.xml.get_widget("labelXPos")
                try: widget.set_text(str(project.current_experiment.point_list[-1].x))
                except: pass
                
                widget = self.xml.get_widget("labelYPos")
                try: widget.set_text(str(project.current_experiment.point_list[-1].y))
                except: pass
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

        widget = self.xml.get_widget("buttonAreas")
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
                 
        widget = self.xml.get_widget("buttonRefImg")
        widget.set_sensitive(False)
        
        widget = self.xml.get_widget("mainNotebook")
        widget.get_nth_page(0).set_sensitive(False)                
                           
        widget = self.xml.get_widget("mainNotebook")
        widget.get_nth_page(2).set_sensitive(False)
                           
    def ready_state(self):        
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)            
        
        widget = self.xml.get_widget("buttonNew")
        widget.set_sensitive(True)        

        widget = self.xml.get_widget("buttonOpen")
        widget.set_sensitive(True)        
        
        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(True)        
        
        if self.project.current_experiment.point_list == [] or \
           self.project.current_experiment.areas_list == []:
            pass
        else:
            widget = self.xml.get_widget("buttonTortuosity")
            widget.set_sensitive(True)        
        
            widget = self.xml.get_widget("buttonReport")
            widget.set_sensitive(True)        
            
            widget = self.xml.get_widget("buttonPrint")
            widget.set_sensitive(True)
            
            if not self.invalid_refimg:
                widget = self.xml.get_widget("buttonProcess")
                widget.set_sensitive(True)
            
        if self.invalid_refimg:
            pass
        else:
            widget = self.xml.get_widget("buttonAreas")
            widget.set_sensitive(True)
                
            widget = self.xml.get_widget("buttonScale")        
            widget.set_sensitive(True)
            
            if self.invalid_scale:
                pass
            else:
                widget = self.xml.get_widget("buttonInsectSize")        
                widget.set_sensitive(True)        
                 
        widget = self.xml.get_widget("buttonRefImg")
        widget.set_sensitive(True)                          
        
        widget = self.xml.get_widget("buttonProjProperties")
        widget.set_sensitive(True)         
            
        widget = self.xml.get_widget("buttonStart")
        if self.invalid_size or self.invalid_areas or \
           self.invalid_scale or self.invalid_speed:
            widget.set_sensitive(False)
        else:
            widget.set_sensitive(True)        
       
        widget = self.xml.get_widget("toggleTimer")
        widget.set_sensitive(True)     
        
        widget = self.xml.get_widget("mainNotebook")
        widget.get_nth_page(0).set_sensitive(True)        
        
        widget = self.xml.get_widget("mainNotebook")
        widget.get_nth_page(2).set_sensitive(True)                
        
           
    def report(self, widget):
        fsdialog = gtk.FileChooserDialog(_("Save Report"), self.window,
                     gtk.FILE_CHOOSER_ACTION_SAVE,
                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OK, gtk.RESPONSE_OK) )        
        if self.project.filename:             
            fsdialog.set_current_folder(self.project.filename)
        else:
            fsdialog.set_current_folder(self.home)
        
        response = fsdialog.run()
        
        if response == gtk.RESPONSE_OK:
            filename = fsdialog.get_filename() + '.csv'
            self.project.export(filename)            
        fsdialog.destroy()
        msg = gtk.MessageDialog ( self.window, 
                                  gtk.DIALOG_DESTROY_WITH_PARENT, 
                                  gtk.MESSAGE_INFO, 
                                  gtk.BUTTONS_OK,
                                  _("Report generated.") )
        msg.run()
        msg.destroy()
    
    def main(self, argv):
        gtk.main()
        

if __name__ == "__main__":
    base = Interface()
    base.main()

