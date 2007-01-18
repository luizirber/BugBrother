#/usr/bin/env python

import gc
gc.set_threshold(100)

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
gobject.threads_init()

import pygst
pygst.require('0.10')
import gst

from kiwi.environ import environ

from sacam.i18n import _, APP_NAME

from sacam.videoprocessor import videoprocessor

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
        
        gladefile = environ.find_resource('glade', 'sacam.glade')
        windowname = "devicemanager"
        self.xml = gtk.glade.XML(gladefile, windowname, domain=APP_NAME)
        self.devicewindow = self.xml.get_widget(windowname)
        self.devicewindow.connect("delete-event", self.delete)
        
        self.processor = videoprocessor()         
        self.outputarea = video_output
        self.outputarea.connect("expose-event", self.expose_cb)
        self.processor_output = processor_output
        self.frame_format = None
        
        #TODO: look for these values, don't hardcode then
        device = '/dev/video0'
        width, height = 640, 480
        
        #TODO: merge the pipelines
        pipeline_string = (
#            'videotestsrc name=source ! ffmpegcolorspace ! '        
            'v4lsrc device=%s name=source ! ffmpegcolorspace ! '
            'video/x-raw-rgb,bpp=24,depth=24,format=RGB24,width=%d,height=%d ! '            
            'identity name=null ! ffmpegcolorspace ! xvimagesink name=sink force-aspect-ratio=true'
#           )%(width, height)
           )%(device,width, height)           
        
#        pipeline_string2 = (
#           'videotestsrc name=source ! xvimagesink name=sink force-aspect-ratio=true'           
#           'v4lsrc device=%s name=source ! xvimagesink name=sink force-aspect-ratio=true'
#        )%(device)
                  
        pipeline = gst.parse_launch(pipeline_string)
#        self.pipeline_play = gst.parse_launch(pipeline_string2)
        self.pipeline_play = pipeline
        self.source = pipeline.get_by_name("source")
#      
        self.null = pipeline.get_by_name("null")
        self.null.connect("handoff", self.frame_setter)
        self.sink = self.pipeline_play.get_by_name("sink")
        
#        self.source = gst.element_factory_make('v4lsrc', "source")
#        self.source.props.device = device
        
#        self.null = gst.element_factory_make('identity', "null")
#        self.null.connect("handoff", self.frame_setter)
        
#        colorspace = gst.element_factory_make('ffmpegcolorspace')
        
#        self.sink = gst.element_factory_make('xvimagesink', "sink")
#        self.sink.props.force_aspect_ratio = True
        
#        pipeline.add(self.source, self.null, colorspace, self.sink) 
#        gst.element_link_many(self.source, self.null, colorspace, self.sink)
        
        bus = pipeline.get_bus()
        bus.add_signal_watch()

#        self.pipeline_capture = pipeline
        self.pipeline_capture = self.pipeline_play
        self.pipeline_capture.set_state(gst.STATE_READY)
        self.pipeline_play.set_state(gst.STATE_READY)

#        chan = self.source.find_channel_by_name('Composite1')
#        self.source.set_channel(chan)       
#        print [param.name for param in self.sink.props]        

#	src = self.pipeline_play.get_by_name("source")
#	chan = src.find_channel_by_name("Composite1")
#	src.set_channel(chan)


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
                    
#        self.pipeline.set_state(gst.STATE_PLAYING)

            
    def expose_cb(self, wid, event):
        self.sink.set_xwindow_id(self.outputarea.window.xid)   
        
    def frame_setter(self, element, buf):
        for structure in buf.caps:
            if structure["format"]=="RGB24":
                if self.frame_format == None:
                    self.frame_format = structure["format"]            
                    self.frame_width = structure["width"]
                    self.frame_height = structure["height"]                
                self.frame = buf.data
            if structure["format"]=="YUV2":
                pass
                
        
    def get_current_frame(self):
        self.pixbuf = gtk.gdk.pixbuf_new_from_data(self.frame, gtk.gdk.COLORSPACE_RGB, 
                        False, 8, self.frame_width, self.frame_height, 
                        self.frame_width*3)
        return self.pixbuf
        
    def start_video(self, widget, project):
#        self.timeout_id = gobject.timeout_add(200, self.processor.process_video,
#                                    self.get_current_frame(),
#                                    self.processor_output, project)
        
        self.processor.process_video(self.get_current_frame(), 
                                     self.processor_output, project)
        return True 
          
    def show_window(self, widget):
        self.devicewindow.show_all()
        #connect the callbacks for the insect size dialog        
        response = self.devicewindow.run()
        
        if response == gtk.RESPONSE_OK :
            # Handle changes in the pipeline
            self.devicewindow.hide_all()
        else:
            self.devicewindow.hide_all()
        
    def delete(self, widget, event):
        self.devicewindow.hide_all()
        