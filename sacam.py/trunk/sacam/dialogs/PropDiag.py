from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from kiwi.environ import environ

from sacam.areas import Ellipse, Rectangle, Area, Line
from sacam.i18n import _, APP_NAME

class PropDiag(object):
    ''' This dialog sets the project properties. '''

    def __init__(self):
        gladefile = environ.find_resource('glade', 'projprop.glade')
        self.gui = gtk.glade.XML(gladefile, domain=APP_NAME)

    def run(self, wid, project):
        ''' Run the specific dialog and save the changes in the project. '''

        propdiag = self.gui.get_widget("dialogProjProp");
        propdiag.show_all()
        experiment = project.current_experiment

        entry_bio = self.gui.get_widget("entryNameProject")
        entry_exp = self.gui.get_widget("entryNameExperiment")
        entry_name = self.gui.get_widget("entryNameInsect")
        entry_comp = self.gui.get_widget("entryComp")
        entry_temp = self.gui.get_widget("entryTemp")
        hscale_threshold = self.gui.get_widget("hscaleThreshold")

        try:
            temp = project.attributes[_("Project Name")]
        except KeyError:
            entry_bio.props.text = ""
        else:
            entry_bio.props.text = temp

        try:
            temp = experiment.attributes[_("Experiment Name")]
        except KeyError:
            entry_exp.props.text = ""
        else:
            entry_exp.props.text = temp

        try:
            temp = project.attributes[_("Insect Name")]
        except KeyError:
            entry_name.props.text = ""
        else:
            entry_name.props.text = temp

        try:
            temp = project.attributes[_("Compounds used")]
        except KeyError:
            entry_comp.props.text = ""
        else:
            entry_comp.props.text = temp

        try:
            temp = project.attributes[_("Temperature")]
        except KeyError:
            entry_temp.props.text = ""
        else:
            entry_temp.props.text = temp

        hscale_threshold.set_value(project.current_experiment.threshold)

        response = propdiag.run()
        if response == gtk.RESPONSE_OK :
            project.attributes[_("Project Name")] = entry_bio.props.text
            project.attributes[_("Insect Name")] = entry_name.props.text
            project.attributes[_("Compounds used")] = entry_comp.props.text
            project.attributes[_("Temperature")] = entry_temp.props.text
            experiment.attributes[_("Experiment Name")] = entry_exp.props.text
            experiment.threshold = hscale_threshold.get_value()
            propdiag.hide_all()
            
            return True
        else:
            propdiag.hide_all()
            return False
