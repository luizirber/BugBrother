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
        
        widget = self.xml.get_widget("buttonProjProperties")
        widget.connect("clicked", self.run_prop_diag)
        
        widget = self.xml.get_widget("buttonAreas")
        widget.connect("clicked", self.run_areas_diag)
        
        widget = self.xml.get_widget("buttonScale")
        widget.connect("clicked", self.run_scale_diag)
        
        widget = self.xml.get_widget("buttonInsectSize")
        widget.connect("clicked", self.run_insect_size_diag)        
        
        self.window.connect("destroy", self.destroy)
        self.window.show()
        
        #refimg area callbacks
        widget = self.xml.get_widget('buttonConfirm')
        widget.connect('clicked', self.refimgCapture)
        
        return
   
    def run_prop_diag(self, wid):
        propdiag = self.xml.get_widget("dialogProjProp"); 
        propdiag.connect('delete-event', self.delete_diag)        
        propdiag.show_all()
        
        entryBio = self.xml.get_widget("entryNameBio")
        entryName = self.xml.get_widget("entryNameInsect")
        entryComp = self.xml.get_widget("entryComp")
        entryTemp = self.xml.get_widget("entryTemp")
        
        try: t = self.project.attributes["Name of the Project"]
        except KeyError: entryBio.props.text = ""
        else: entryBio.props.text = t
        
        try: t = self.project.attributes["Name of Insect"]
        except KeyError: entryName.props.text = ""
        else: entryName.props.text = t
            
        try: t = self.project.attributes["Compounds used"]
        except KeyError: entryComp.props.text = ""
        else: entryComp.props.text = t
        
        try: t = self.project.attributes["Temperature"]
        except KeyError: entryTemp.props.text = ""
        else: entryTemp.props.text = t
            
        response = propdiag.run()        
        if response == gtk.RESPONSE_OK :
            self.project.attributes["Name of the Project"] = entryBio.props.text
            self.project.attributes["Name of Insect"] = entryName.props.text
            self.project.attributes["Compounds used"] = entryComp.props.text
            self.project.attributes["Temperature"] = entryTemp.props.text
            propdiag.hide_all()
            return True
        else:
            propdiag.hide_all()            
            return False     
     
    def run_refimg_diag(self, wid):
        refimgDiag = self.xml.get_widget("dialogRefImage");                 
        refimgDiag.connect('delete-event', self.delete_diag)       
        refimgDiag.show_all()        
        response = refimgDiag.run()
                
        if response == gtk.RESPONSE_OK :
            refimgDiag.hide_all()
            return True
        else:
            refimgdiag.hide_all()            
            self.invalid_refimage = True
            return False
        
    def run_areas_diag(self, wid):
        areasDiag = self.xml.get_widget("dialogAreas"); 
        areasDiag.connect('delete-event', self.delete_diag)        
        areasDiag.show_all()        
        #connect the callbacks for the areas dialog        
        response = areasDiag.run()
        
        if response == gtk.RESPONSE_OK :
            areasDiag.hide_all()
            return True
        else:
            areasDiag.hide_all()            
            self.invalid_areas = True
            return False
        
    def run_scale_diag(self, wid):
        scaleDiag = self.xml.get_widget("dialogScale"); 
        scaleDiag.connect('delete-event', self.delete_diag)        
        scaleDiag.show_all()        
        #connect the callbacks for the scale dialog        
        response = scaleDiag.run()
        
        if response == gtk.RESPONSE_OK :
            #save the scale
            scaleDiag.hide_all()
            return True
        else:
            scaleDiag.hide_all()            
            self.invalid_scale = True
            return False
        
    def run_insect_size_diag(self, wid):
        insectSizeDiag = self.xml.get_widget("dialogInsectSize"); 
        insectSizeDiag.connect('delete-event', self.delete_diag)        
        insectSizeDiag.show_all()
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
            insectSizeDiag.hide_all()            
            self.invalid_size = True
            return False
                
    def main(self):
        gtk.main()

    def save_project(self, widget):
        if self.invalid_path:
            #handle this
            pass
        self.project.save()

    def destroy(self, widget):
        gtk.main_quit()
        
    def delete_diag(self, diag, event):
        diag.hide_all()
     
    def new_project(self, widget):
        main = self.xml.get_widget("mainwindow")
        
        fsdialog = gtk.FileChooserDialog("New Project", main,
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
        
        response = self.run_prop_diag(None)
        
        if response == False :
            self.ready_state()            
            return
               
        self.device_manager.pipeline_capture.set_state(gst.STATE_PLAYING)      
        self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)
       
        self.device_manager.sink.set_xwindow_id(
                                    self.device_manager.outputarea.window.xid)
                
        response = self.run_refimg_diag(None)
        if response == False :
            self.ready_state()            
            return
        
        response = self.run_areas_diag(None)
        if response == False :
            self.ready_state()            
            return

        response = self.run_scale_diag(None)
        if response == False :
            self.ready_state()
            return
                
        response = self.run_insect_size_diag(None)
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
            self.ready_state()            
        fsdial.destroy()
        
        if self.project.filename:
            self.project.load()
            
        #take this out when release the code
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
        
    def process(self, widget):
        pass
         #PrepararGradeApresentacaoEstatisticas
             #Para cada area
                #HoraInicio
                #HoraFim
                #Permanencia (Fim - Inicio)
                #Trajeto
                #VelLinearMedia
                #DesvPadrao - VelLinear
                #VelAngularMedia
                #DesvPadrao - VelAngular
                #Tortuosidade
                
         #PrepararGradeApresentacaoSintese
            #Area
            #Tempo de permanencia
            #Tempo(%)
            #TrajetoTotal (cm)
            #Trajeto (%)
           #calcular para point_list do experimento 
            #TempoTotal
            #ComprimentoTotal

if __name__ == "__main__":
    base = Interface()
    base.main()
