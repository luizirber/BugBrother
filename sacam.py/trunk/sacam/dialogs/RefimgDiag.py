from math import sqrt

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from kiwi.environ import environ

from sacam.areas import Ellipse, Rectangle, Area, Line
from sacam.i18n import _, APP_NAME

class RefimgDiag(object):
    ''' This dialog contains the code to capture a pixbuf and save it as the
        reference image for the project. '''

    def __init__(self):
        gladefile = environ.find_resource('glade', 'refimg.glade')
        self.xml = gtk.glade.XML(gladefile, domain=APP_NAME)

    def run(self, wid, project, device, interface):
        ''' Run the specific dialog and save the changes in the project. '''

        widget = self.xml.get_widget('buttonConfirm')
        widget.connect('clicked', self.capture, project, device)

        refimg_widget = self.xml.get_widget("imageRefImg")
        if project.refimage:
            refimg_widget.set_from_pixbuf(project.refimage)
        refimg_widget.set_size_request(device.frame['width'],
                                       device.frame['height'])

        refimg_diag = self.xml.get_widget("dialogRefImage");
        refimg_diag.show_all()
        response = refimg_diag.run()

        if response == gtk.RESPONSE_OK :
            refimg = refimg_widget.get_pixbuf()
            if refimg:
                project.refimage = refimg
            refimg_diag.hide_all()
            interface.update_state()
            return True
        else:
            refimg_diag.hide_all()
            interface.update_state()
            return False

    def capture(self, widget, project, device):
        ''' Get the image from the device and show on the screen. '''

        image = self.xml.get_widget('imageRefImg')
        project.refimage = device.get_current_frame()
        image.set_from_pixbuf(project.refimage)
