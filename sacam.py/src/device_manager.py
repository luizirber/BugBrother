#/usr/bin/env python

from sys import platform
from random import choice

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import gtk.glade
import gobject

import pygst
pygst.require('0.10')
import gst

class Device_manager(object):
   
    xml = None
    xid = None
    pipeline = None
    source = None
    sink = None
    gladefile = None
    devicewindow = None
    outputarea = None
           
    # TODO: see flumotion/component/producers/bttv/bttv.py 
    # and optimize this    
    def __init__(self, output):
        
        gladefile = "sacam.glade"
        windowname = "devicemanager"
        self.xml = gtk.glade.XML(gladefile, windowname)
        self.devicewindow = self.xml.get_widget(windowname)
        self.devicewindow.connect("destroy", self.destroy)
        
        self.outputarea = output
        
        device = '/dev/video0'
        width, height = 320, 240
        framerate_string = '25/1'
        
        pipeline_string = ('playbin')
#        pipeline_string =  ('v4l2src name=source device=%s '
#                           '! video/x-raw-rgb,format=RGB24,width=%s,height=%s'
#                           ',framerate=%s'
#                           '! ffmpegcolorspace '
#                           '! tee name=tee '
#                           'tee. ! gdkpixbufdec name=pixbuf '
#                           'tee. ! xvimagesink name=sink force-aspect-ratio=true ') \
#                          % (device,width,height)#,framerate_string)
                          
        pipeline = gst.parse_launch(pipeline_string)
#        pipeline = gst.element_factory_make("playbin", "player")
#        pipeline.set_property('source', gst.element_factory_make("v4lsrc"))
#        self.source = pipeline.props.source

#
#       A Solution: gst_pad_add_buffer_probe
#
        self.sink = pipeline.get_by_name("video-sink")
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        watch_id = bus.connect('message', self.on_message)
        self.pipeline = pipeline
        self.watch_id = watch_id
        self.pipeline.set_state(gst.STATE_PAUSED)

#        chan = self.source.find_channel_by_name('Composite1')
#        self.source.set_channel(chan)       
#        print [param.name for param in self.sink.props]        

#        cell = gtk.CellRendererText()
        
#        combodevice = self.xml.get_widget("comboDevice")
#        deviceliststore = gtk.ListStore(gobject.TYPE_STRING)        
        
#        combochannel = self.xml.get_widget("comboChannel")
#        channelliststore = gtk.ListStore(gobject.TYPE_STRING)        
        
#        combonorm = self.xml.get_widget("comboNorm")                        
#        normliststore = gtk.ListStore(gobject.TYPE_STRING)
        
#        comboformat = self.xml.get_widget("comboFormat")                        
#        formatliststore = gtk.ListStore(gobject.TYPE_STRING)
        
#        liststore = { combodevice:deviceliststore, combochannel:channelliststore,
#                      combonorm:normliststore, comboformat:formatliststore }

#        for comboitem in liststore:
#            comboitem.set_model(liststore[comboitem])
#            comboitem.pack_start(cell, True)
#            comboitem.add_attribute(cell, 'text', 0)
        
#        channels = [channel.label for channel in self.source.list_channels()]
#        for item in channels:
#            combochannel.append_text(item)
                
#        norms = [norm.label for norm in self.source.list_norms()]
#        for item in norms:
#            combonorm.append_text(item)
            
#        possibilities = []            
#        capstring = [param.get_caps().to_string() for param in self.source.pads()]
#        caps = capstring[0].split(';')
#        for item in caps:
#            comboformat.append_text(item)
#            possibilities.append(item.split())
            
#        for item in possibilities:
#            pass            
       
        return
        
    def on_message(self, bus, message):
        t = message.type

        if t == gst.MESSAGE_ELEMENT:
            if message.structure:
                if platform=='win32':                
                    self.outputarea.set_xid(message.structure["handle"])
                else:
#                    self.outputarea.set_xid(message.structure["xwindow-id"])
                    self.xid = message.structure["xwindow-id"]
                    
        return True        
          
    def on_timeout(self, *args):
#        temp = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,0,8,
#                              640, 480)
#        colormap = self.outputarea.window.get_colormap()
#        temp = temp.get_from_drawable(self.outputarea.window, 
#                                      colormap, 0, 0, 0, 0, -1, -1)
#        filename = "teste" + str(choice(range(1, 20))) + '.jpg'
#        temp.save(filename, "jpeg", {"quality":"100"})
#        print filename
        return True
          
    def start_video(self, widget):
        self.get_current_frame()
        self.sink.set_xwindow_id(self.outputarea.window.xid)
        self.pipeline.set_state(gst.STATE_PLAYING)
        if ( widget.get_active() ):
            self.timeout_id = gobject.timeout_add(1000, self.on_timeout)
        else:
            gobject.source_remove(self.timeout_id)
            
    def get_current_frame(self):
        temp = self.pipeline.props.frame
        print temp                   
                   
    def show_window(self, widget):
        self.devicewindow.show_all()
        
    def destroy(self, widget):
        self.devicewindow.hide_all()
                             
    def __del__(self):
        self.pipeline.set_state(gst.STATE_NULL)
        