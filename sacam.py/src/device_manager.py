#/usr/bin/env python

from sys import platform
from random import choice
import gc
gc.set_threshold(100)

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import gtk.glade
import gobject
gobject.threads_init()

import pygst
pygst.require('0.10')
import gst

from videoprocessor import videoprocessor

class Device_manager(object):
   
    xml = None
    xid = None
    pipeline = None
    source = None
    sink = None
    gladefile = None
    devicewindow = None
    outputarea = None
    frame = None
    pixbuf = None
           
    def __init__(self, video_output, processor_output):
        
        gladefile = "sacam.glade"
        windowname = "devicemanager"
        self.xml = gtk.glade.XML(gladefile, windowname)
        self.devicewindow = self.xml.get_widget(windowname)
        self.devicewindow.connect("destroy", self.destroy)
        
        self.processor = videoprocessor()         
        self.outputarea = video_output
        self.processor_output = processor_output
        
        device = '/dev/video0'
        width, height = 640, 480
        
        pipeline_string = ('videotestsrc name=source ! '
                           #'v4lsrc device=/dev/video0 name=source ! '
                           'video/x-raw-rgb,bpp=24,depth=24,format=RGB24,width=%s,height=%s !'
                           'identity name=null ! ffmpegcolorspace ! ' 
                           'xvimagesink name=sink force-aspect-ratio=true'
                          ) % (width,height)
                          
        pipeline = gst.parse_launch(pipeline_string)
        self.source = pipeline.get_by_name("source") 
        self.null = pipeline.get_by_name("null")
        self.null.connect("handoff", self.frame_setter)
        self.sink = pipeline.get_by_name("sink")
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        self.pipeline = pipeline
        self.pipeline.set_state(gst.STATE_READY)

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
        
#        liststore = { combodevice:deviceliststore, combochannel:channelliststore,
#                      combonorm:normliststore }

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
            
        
    def frame_setter(self, element, buf):
        structure = buf.caps[0]
        if structure["format"]=="RGB24":
            self.frame = buf.data
            self.frame_format = structure["format"]            
            self.frame_width = structure["width"]
            self.frame_height = structure["height"]
        
    def get_current_frame(self):
        self.pixbuf = gtk.gdk.pixbuf_new_from_data(self.frame, gtk.gdk.COLORSPACE_RGB, 
                        False, 8, self.frame_width, self.frame_height, 
                        self.frame_width*3)
        return self.pixbuf
        
    def start_video(self, widget, project):
#        self.timeout_id = gobject.timeout_add(2000, self.processor.process_video,
#                                    self.get_current_frame(),
#                                    self.processor_output, experiment)

         self.processor.process_video(self.get_current_frame(), 
                                    self.processor_output, project)
           
    def show_window(self, widget):
        self.devicewindow.show_all()
        
    def destroy(self, widget):
        self.devicewindow.hide_all()
                             
    def __del__(self):
        self.pipeline.set_state(gst.STATE_NULL)
        