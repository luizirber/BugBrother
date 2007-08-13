import gtk
import gobject

from sacam.i18n import _

class ProjectManager(object):

    def __init__(self, xml, project):
        self.xml = xml
        self.project = project
        self.edited_hndl = None
        view = self.xml.get_widget("treeviewPrjManager")
        model = gtk.TreeStore( gobject.TYPE_STRING,
                               gobject.TYPE_PYOBJECT )
        self.populate(view, None, model)

        # renderer of the first column
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        view.append_column(column)
        view.set_expander_column(column)

        # treat single selection only
        selection = view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)

        # TODO: this signal will determine the right side of the manager
        # (wheter to show properties from track, area, exp or project).
        view.connect("cursor_changed", self.changed_cursor_cb)

        view.connect("visibility-notify-event", self.populate, model)

    def populate(self, view, event, model):
        model.clear()
        project = model.append( None,
                                [ self.project.attributes[_("Project Name")],
                                  self.project ]
                              )
        for exp in self.project.exp_list:
            parent = model.append( project,
                                   [ exp.attributes[_("Experiment Name")],
                                     exp ]
                                 )
            for area in exp.areas_list:
                area_parent = model.append( parent, [area.name, area] )
                for track in area.track_list:
                    model.append( area_parent,
                                  [ str(track.start_time.time()), track ] )
        view.set_model(model)
        view.expand_all()

    def set_project(self, prj):
        self.project = prj

    def changed_cursor_cb(self, view):
        ''' Select an area in the treeview to be changed. '''

        selection = view.get_selection()
        model, treeiter = selection.get_selected()
        depth = model.iter_depth(treeiter)
        entry = self.xml.get_widget("entryManagerName")
        if self.edited_hndl:
            entry.disconnect(self.edited_hndl)
        selected = model.get_value(treeiter, 1)
        self.edited_hndl = entry.connect("activate", self.edited_cb,
                                          selected, depth)

    def edited_cb(self, entry, obj, depth):
        entry.set_sensitive(True)
        if depth == 0:
            #project object
            obj.attributes[_("Project Name")] = entry.get_text()
        elif depth == 1:
            #exp object
            obj.attributes[_("Experiment Name")] = entry.get_text()
        elif depth == 2:
            #area object
            obj.name = entry.get_text()
        elif depth == 3:
            #track object
            entry.set_sensitive(False)

