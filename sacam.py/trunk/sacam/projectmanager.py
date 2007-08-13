import gtk
import gobject

from sacam.i18n import _

class ProjectManager(object):

    def __init__(self, xml, project):
        self.xml = xml
        self.project = prj

    def populate_tree(self):
        for exp in self.project.exp_list:
            pass

    def set_project(self, prj):
        self.project = prj
