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
        
        self.device = '/dev/video0'
        self.width, self.height = 640, 480
        
        self.pipeline_play = None
        
        widget = self.xml.get_widget('buttonDefaultPipeline')
        widget.connect('clicked', self.set_default_pipeline_string)
        
        widget = self.xml.get_widget('buttonTestingPipeline')
        widget.connect('clicked', self.set_testing_pipeline_string)
                
        self.counter = 0
        
        widget = self.xml.get_widget('comboboxInputType')
        widget.connect('changed', self.combo_change)

        self.textview = self.xml.get_widget("textviewPipeline")
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.set_testing_pipeline_string(None)
        #self.set_default_pipeline_string(None)
        if not self.set_pipelines():
            print 'error!'
            
    def set_default_pipeline_string(self, button):
        pipeline_string = (
            'v4lsrc device=%s name=source ! ffmpegcolorspace ! '
            'video/x-raw-rgb,bpp=24,depth=24,format=RGB24,width=%d,height=%d ! '            
            'identity name=null ! ffmpegcolorspace ! '
           )%(self.device, self.width, self.height)
        
        pipeline_string2 = (
           'v4lsrc device=%s name=source ! '
        )%(self.device)

        self.pipeline_string = pipeline_string
        self.textview.get_buffer().set_text(pipeline_string)
        
    def set_testing_pipeline_string(self, button):                
        pipeline_string = (
            'videotestsrc name=source ! ffmpegcolorspace ! '                
            'video/x-raw-rgb,bpp=24,depth=24,format=RGB24,width=%d,height=%d ! '
            'identity name=null ! ffmpegcolorspace ! '
           )%(self.width, self.height)
        self.pipeline_string = pipeline_string
        self.textview.get_buffer().set_text(pipeline_string)    
            
    def set_pipelines(self):
        fake_sink = 'fakesink'
        video_sink = 'xvimagesink name=sink force-aspect-ratio=true'
        pipeline = gst.parse_launch(self.pipeline_string + fake_sink)
#        self.pipeline_play = gst.parse_launch(pipeline_string2)
        state_change = pipeline.set_state(gst.STATE_PAUSED)

        if state_change == gst.STATE_CHANGE_FAILURE:
            return False
        else:
            if self.pipeline_play:
                self.pipeline_play.set_state(gst.STATE_NULL)
    	    pipeline.set_state(gst.STATE_NULL)
    	    pipeline = gst.parse_launch(self.pipeline_string + video_sink)
            
        self.pipeline_play = pipeline
        self.source = pipeline.get_by_name("source")

        self.null = pipeline.get_by_name("null")
        self.null.connect("handoff", self.frame_setter)
        self.sink = self.pipeline_play.get_by_name("sink")
                
        bus = pipeline.get_bus()
        bus.add_signal_watch()

#        self.pipeline_capture = pipeline
        self.pipeline_capture = self.pipeline_play
        self.pipeline_capture.set_state(gst.STATE_PLAYING)
        self.pipeline_play.set_state(gst.STATE_PLAYING)

        return True
                    
    def pipeline_start(self):
	self.pipeline_capture.set_state(gst.STATE_PLAYING)
        self.pipeline_play.set_state(gst.STATE_PLAYING)

    def pipeline_destroy(self):
    	self.pipeline_capture.set_state(gst.STATE_NULL)
	self.pipeline_play.set_state(gst.STATE_NULL)

    def expose_cb(self, wid, event):
        self.sink.set_xwindow_id(self.outputarea.window.xid)   

    def bttv_options_setter(self):
        pass
    #        chan = self.source.find_channel_by_name('Composite1')
#        self.source.set_channel(chan)       
#        print [param.name for param in self.sink.props]        

#   src = self.pipeline_play.get_by_name("source")
#   chan = src.find_channel_by_name("Composite1")
#   src.set_channel(chan)


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
        self.counter += 1
        if self.counter == 10:
            gc.collect()
            self.counter = 0
                                             
        return True 
          
    def combo_change(self, combo):
        option = combo.get_active()

        widget = self.xml.get_widget('vboxBttv')
        widget.props.visible = False
        
        widget = self.xml.get_widget('vboxWebcam')
        widget.props.visible = False

        if option == 0:
            # bttv selected
            box = self.xml.get_widget('vboxBttv')
            box.props.visible = True
            self.width = 640
            self.height = 480
            self.device = '/dev/video0'
            self.set_default_pipeline_string(None)
        elif option == 1:
            # webcam selected
            box = self.xml.get_widget('vboxWebcam')
            box.props.visible = True            
            self.width = 320
            self.height = 240
            self.device = '/dev/video0'
            self.set_default_pipeline_string(None)
        elif option == 2:
            # firewire selected
            print 'not implemented yet'
          
    def show_window(self, widget):
        self.devicewindow.show_all()        
        response = self.devicewindow.run()
        if response == gtk.RESPONSE_OK :
            # Handle changes in the pipeline   
            self.set_pipelines()
            self.devicewindow.hide_all()
        else:
            self.devicewindow.hide_all()
        
    def delete(self, widget, event):
        self.devicewindow.hide_all()
        
