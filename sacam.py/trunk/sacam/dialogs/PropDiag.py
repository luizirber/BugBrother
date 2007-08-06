from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from sacam.areas import Ellipse, Rectangle, Area, Line

from sacam.i18n import _

class PropDiag(object):
    ''' This dialog sets the project properties. '''

    def run(self, wid, project, xml):
        ''' Run the specific dialog and save the changes in the project. '''

        propdiag = xml.get_widget("dialogProjProp");
        propdiag.show_all()
        experiment = project.current_experiment

        entry_bio = xml.get_widget("entryNameProject")
        entry_exp = xml.get_widget("entryNameExperiment")
        entry_name = xml.get_widget("entryNameInsect")
        entry_comp = xml.get_widget("entryComp")
        entry_temp = xml.get_widget("entryTemp")
        hscale_threshold = xml.get_widget("hscaleThreshold")

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
            window = xml.get_widget("mainwindow")
            window.set_title( ("SACAM - %s - %s") %
                              ( project.attributes[_("Project Name")] ,
                                experiment.attributes[_("Experiment Name")] ) )
            return True
        else:
            propdiag.hide_all()
            return False
