from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from kiwi.environ import environ

from sacam.areas import Ellipse, Rectangle, Area, Line
from sacam.i18n import _, APP_NAME

class InsectsizeDiag(object):
    ''' Dialog that control the insect size and speed, parameters
        needed to make the videoprocessor faster. '''

    def __init__(self):
        gladefile = environ.find_resource('glade', 'insectsize.glade')
        self.xml = gtk.glade.XML(gladefile, domain=APP_NAME)

        self.project = None
    
    def run(self, wid, project, interface):
        ''' Run the specific dialog and save the changes in the project. '''

        self.project = project
        insectsize_diag = self.xml.get_widget("dialogInsectSize");
        
        value = self.project.current_experiment.measurement_unit
        self.xml.get_widget("labelSize").set_label(value)
        self.xml.get_widget("labelSpeed").set_label(value + "/s")
        
        # Snoop Dogg mode ON
        x_scale = self.project.current_experiment.x_scale_ratio
        y_scale = self.project.current_experiment.y_scale_ratio
        if x_scale > y_scale:
            siz = self.project.bug_size / x_scale
            spee = self.project.bug_max_speed / x_scale
        else:
            siz = self.project.bug_size / y_scale
            spee = self.project.bug_max_speed / x_scale
        self.xml.get_widget("entryInsectSize").set_text(str(siz))
        self.xml.get_widget("entryInsectSpeed").set_text(str(spee))
        #Snoop Dogg mode OFF
        
        insectsize_diag.show_all()
        response = insectsize_diag.run()
        if response == gtk.RESPONSE_OK :
            widget = self.xml.get_widget("entryInsectSize")
            try:
                size = float(widget.props.text)
            except ValueError:
                pass
            else:
                self.project.original_bug_size = size
                x_scale = self.project.current_experiment.x_scale_ratio
                y_scale = self.project.current_experiment.y_scale_ratio
                if x_scale > y_scale:
                    size *= self.project.current_experiment.x_scale_ratio
                else:
                    size *= self.project.current_experiment.y_scale_ratio
                self.project.bug_size = size
            
            widget = self.xml.get_widget("entryInsectSpeed")
            try:
                speed = float(widget.props.text)
            except ValueError:
                pass
            else:
                self.project.original_bug_speed = speed
                x_scale = self.project.current_experiment.x_scale_ratio
                y_scale = self.project.current_experiment.y_scale_ratio
                if x_scale > y_scale:
                    speed *= self.project.current_experiment.x_scale_ratio
                else:
                    speed *= self.project.current_experiment.y_scale_ratio
                self.project.bug_max_speed = speed
                
            insectsize_diag.hide_all()
            interface.update_state()
            return True
        else:
            insectsize_diag.hide_all()
            interface.update_state()
            return False
