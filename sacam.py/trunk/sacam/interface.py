''' Main module, it manages the relationship of the others.'''

import os
from datetime import datetime

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import pygst
pygst.require('0.10')
import gst

from kiwi.environ import environ
from sacam.i18n import _, APP_NAME

from sacam.device_manager import DeviceManager
from sacam.project import Project
from sacam.dialogs import PropDiag, RefimgDiag, AreasDiag
from sacam.dialogs import ScaleDiag, InsectsizeDiag
from sacam.tracksimulator import TrackSimulator
from sacam.projectmanager import ProjectManager

class Interface(object):
    ''' Main class, control the interface of the program.

        Composed of various classes.'''

    def __init__(self):

        gladefile = environ.find_resource('glade', 'sacam.glade')
        windowname = "mainwindow"

        self.xml = gtk.glade.XML(gladefile, domain=APP_NAME)
        self.window = self.xml.get_widget(windowname)

        outputarea = self.xml.get_widget("videoOutputArea")
        self.device_manager = DeviceManager(outputarea)
        self.device_manager.connect_processor_props(self.xml)
        self.running = None

        self.project = Project()
        self.project.current_experiment.release_area = [ 0, 0,
                                         self.device_manager.frame["width"],
                                         self.device_manager.frame["height"] ]

        self.propdiag = PropDiag.PropDiag()
        self.refimgdiag = RefimgDiag.RefimgDiag(self.xml)
        self.areasdiag = AreasDiag.AreasDiag(self.project, self.xml)
        self.scalediag = ScaleDiag.ScaleDiag(self.xml, self.project)
        self.insectsizediag = InsectsizeDiag.InsectsizeDiag(self.xml)
        self.tracksimulator = TrackSimulator(self.xml, self.project,
                                             self.device_manager)
        self.projectmanager = ProjectManager(self.xml, self.project)

        widget = self.xml.get_widget("buttonNew")
        widget.connect("clicked", self.new_project)

        widget = self.xml.get_widget("buttonPreferences")
        widget.connect("clicked", self.device_manager.show_window)

        widget = self.xml.get_widget("buttonSave")
        widget.connect("clicked", self.save_project)

        widget = self.xml.get_widget("buttonOpen")
        widget.connect("clicked", self.load_project)

        widget = self.xml.get_widget("buttonProcess")
        widget.connect("clicked", self.process_lists)

        widget = self.xml.get_widget("buttonReport")
        widget.connect("clicked", self.report)

        self.video_hnd = None
        self.prop_hnd = None
        self.scale_hnd = None
        self.size_hnd = None
        self.refimg_hnd = None
        self.areas_hnd = None
        self.connect_project_signals()

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

        self.project.refimage = self.device_manager.get_current_frame()

        self.window.connect("destroy", self.destroy)
        self.window.show()

        self.update_state()

    def main(self, argv):
        ''' Start the gtk main loop. '''
        gtk.main()

    def connect_project_signals(self):
        ''' Reconnect signals that refers to the current project.

            Every time a project is created, some signals need to be
            reconnected. '''

        widget = self.xml.get_widget("buttonStart")
        if self.video_hnd:
            widget.disconnect(self.video_hnd)
        self.video_hnd = widget.connect("clicked", self.start_video,
                                         self.project)

        widget = self.xml.get_widget("buttonProjProperties")
        if self.prop_hnd:
            widget.disconnect(self.prop_hnd)
        self.prop_hnd = widget.connect("clicked", self.propdiag.run,
                                        self.project, self.xml)

        widget = self.xml.get_widget("buttonScale")
        if self.scale_hnd:
            widget.disconnect(self.scale_hnd)
        self.scale_hnd = widget.connect("clicked", self.scalediag.run,
                                         self.project, self)

        widget = self.xml.get_widget("buttonInsectSize")
        if self.size_hnd:
            widget.disconnect(self.size_hnd)
        self.size_hnd = widget.connect("clicked", self.insectsizediag.run,
                                        self.project, self)

        widget = self.xml.get_widget("buttonRefImg")
        if self.refimg_hnd:
            widget.disconnect(self.refimg_hnd)
        self.refimg_hnd = widget.connect("clicked", self.refimgdiag.run,
                                          self.project, self.device_manager,
                                          self)

        widget = self.xml.get_widget("buttonAreas")
        if self.areas_hnd:
            widget.disconnect(self.areas_hnd)
        self.areas_hnd = widget.connect("clicked", self.areasdiag.run,
                                         self.project, self)
        self.tracksimulator.set_project(self.project)

    def new_project(self, widget):
        ''' Creates a new project.

            Asks the user if he wants to save the
            current project, and deals with the answer.
        '''
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
                self.project = Project()
            else:
                diag.destroy()
                self.project = Project()

        response = self.propdiag.run(None, self.project, self.xml)

        if response == False :
            self.update_state()
            return

        self.device_manager.pipeline_start()

        response = self.refimgdiag.run(None, self.project,
                                       self.device_manager, self)
        if response == False :
            self.update_state()
            return

        response = self.areasdiag.run(None, self.project, self)
        if response == False :
            self.update_state()
            return

        response = self.scalediag.run(None, self.project, self)
        if response == False :
            self.update_state()
            return

        response = self.insectsizediag.run(None, self.project, self)
        if response == False :
            self.update_state()
            return

        self.update_state()

    def load_project(self, widget):
        ''' Shows the load dialog.

            Asks the user the filename of the project,
            and load it.
        '''
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
            self.update_state()
            fsdial.destroy()

        if filename:
            prj = self.project.load(filename)
            if prj:
                self.project = prj
                self.update_state()
            else:
                # TODO: print error
                print "error loading project"

    def save_project(self, widget):
        ''' Shows the save dialog.

            Asks the user where to save the project,
            and save it.
        '''
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

    def start_video(self, widget, prj):
        ''' Start the capturing process. '''

        notebook = self.xml.get_widget("mainNotebook")
        notebook.set_current_page(0)

        self.capturing_state()

        if self.device_manager.pipeline_play.get_state() != gst.STATE_PLAYING:
            self.device_manager.pipeline_play.set_state(gst.STATE_PLAYING)

        if widget.get_active():
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_MEDIA_STOP,
                                 gtk.ICON_SIZE_SMALL_TOOLBAR)
            widget.set_image(image)
            if self.invalid_areas:
                self.device_manager.start_video(prj, wait_click=True)
            else:
                self.device_manager.start_video(prj, wait_click=False)
        else:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_MEDIA_PLAY,
                             gtk.ICON_SIZE_SMALL_TOOLBAR)
            widget.set_image(image)
            self.device_manager.stop_video(prj)
            self.project.current_experiment.finished = True
            prj.new_experiment_from_current()
            self.update_state()

    def report(self, widget):
        ''' Shows the report dialog. '''
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

    def process_lists(self, wid):
        ''' Prepare and process the lists to generate statistics.

            It is executed in every experiment present in the project.'''
        for exp in self.project.exp_list:
            if exp.finished:
                exp.prepare_areas_list()
                exp.prepare_stats()

    def update_state(self):
        ''' Verify if the project values are consistent and update the
            user interface. '''
        if len(self.project.current_experiment.areas_list) == 0:
            self.invalid_areas = True
        else:
            self.invalid_areas = False

        if self.project.refimage:
            self.invalid_refimg = False
        else:
            self.invalid_refimg = True

        if self.project.filename:
            if os.path.exists(self.project.filename):
                self.invalid_path = False
            else:
                self.invalid_path = True

        if self.project.bug_size:
            self.invalid_size = False
        else:
            self.invalid_size = True

        if self.project.bug_max_speed:
            self.invalid_speed = False
        else:
            self.invalid_speed = True

        if ( self.project.current_experiment.x_scale_ratio
             and self.project.current_experiment.y_scale_ratio ):
            self.invalid_scale = False
        else:
            self.invalid_scale = True

        if not self.invalid_scale:
            scale = self.project.current_experiment.x_scale_ratio
            if not self.invalid_size:
                widget = self.xml.get_widget("scaleSize")
                widget.set_range(0, self.device_manager.frame["width"] / scale)
                widget.set_value(self.project.bug_size / scale)
                widget = self.xml.get_widget("scaleTolerance")
                widget.set_range(0, self.device_manager.frame["width"] / scale)
                widget.set_value(self.project.bug_size / scale / 2)
            if not self.invalid_speed:
                widget = self.xml.get_widget("scaleSpeed")
                widget.set_range(0, self.device_manager.frame["width"] / scale)
                widget.set_value(self.project.bug_max_speed / scale)

                widget = self.xml.get_widget("labelSize")
                widget.set_text( _("Size (") +
                        self.project.current_experiment.measurement_unit +
                        (") :") )
                widget = self.xml.get_widget("labelSpeed")
                widget = self.xml.get_widget("labelTolerance")

        self.connect_project_signals()

        prj = self.project.attributes[_("Project Name")]
        exp = self.project.current_experiment.attributes[_("Experiment Name")]
        self.window.set_title( ("SACAM - %s - %s") % (prj, exp) )

        self.ready_state()

    def capturing_state(self):
        ''' Set the user interface to capture mode, disabling some options. '''
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
        widget.get_nth_page(1).set_sensitive(False)
        widget.get_nth_page(2).set_sensitive(False)

        self.xml.get_widget("vboxProps").set_sensitive(True)

    def ready_state(self):
        ''' Do the verifications needed to determinate if the capture process
            can be executed. '''
        self.device_manager.pipeline_start()

        widget = self.xml.get_widget("buttonNew")
        widget.set_sensitive(True)

        widget = self.xml.get_widget("buttonOpen")
        widget.set_sensitive(True)

        widget = self.xml.get_widget("buttonSave")
        widget.set_sensitive(True)

#        if ( self.project.current_experiment.point_list == [] or
#             self.project.current_experiment.areas_list == [] ):
#            pass
#        else:
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
        if self.invalid_size or self.invalid_scale or self.invalid_speed:
            widget.set_sensitive(False)
        else:
            widget.set_sensitive(True)

        widget = self.xml.get_widget("toggleTimer")
        widget.set_sensitive(True)

        widget = self.xml.get_widget("mainNotebook")
        widget.get_nth_page(1).set_sensitive(True)
        widget.get_nth_page(2).set_sensitive(True)

#        self.xml.get_widget("vboxProps").set_sensitive(False)

    def destroy(self, widget):
        ''' Stop the pipelines and quit the gtk main loop. '''
        self.device_manager.pipeline_destroy()
        gtk.main_quit()

if __name__ == "__main__":
    BASE = Interface()
    BASE.main()

