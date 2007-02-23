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
        self.width, self.height = 320, 240
        self.norm, self.channel = None, None
        
        self.pipeline_play = None
        
        widget = self.xml.get_widget('buttonDefaultPipeline')
        widget.connect('clicked', self.set_default_pipeline_string)
        
        widget = self.xml.get_widget('buttonTestingPipeline')
        widget.connect('clicked', self.set_testing_pipeline_string)
                
        self.counter = 0
        
        input_type = self.xml.get_widget('comboboxInputType')
        input_type.set_active(0)
        input_type.connect('changed', self.input_combo_change)

        widget = self.xml.get_widget('comboboxWidth')
        input_type.connect('changed', self.set_combo_width, widget)
        widget.connect('changed', self.combo_width_change)

        widget = self.xml.get_widget('comboboxHeight')
        input_type.connect('changed', self.set_combo_height, widget)
        widget.connect('changed', self.combo_height_change)

        widget = self.xml.get_widget('comboboxDevice')
        input_type.connect('changed', self.set_combo_device, widget)
        widget.connect('changed', self.combo_device_change)

        widget = self.xml.get_widget('comboboxChannel')
        input_type.connect('changed', self.set_combo_channel, widget)
        widget.connect('changed', self.combo_channel_change)

        widget = self.xml.get_widget('comboboxNorm')
        input_type.connect('changed', self.set_combo_norm, widget)
        widget.connect('changed', self.combo_norm_change)

        self.textview = self.xml.get_widget("textviewPipeline")
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.set_testing_pipeline_string(None)
        self.show_window(None)
        #self.set_default_pipeline_string(None)
        if not self.set_pipelines():
            print 'error!'
            
    def set_default_pipeline_string(self, button):
        pipeline_string = (
            'v4lsrc device=%s name=source ! ffmpegcolorspace ! '
            'video/x-raw-rgb,bpp=24,depth=24,format=RGB24,width=%d,height=%d ! '            
            'identity name=null ! ffmpegcolorspace ! '
           )%(self.device, self.width, self.height)
        
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
        state_change = pipeline.set_state(gst.STATE_PAUSED)

        if state_change == gst.STATE_CHANGE_FAILURE:
            print 'error! cannot set pipeline'
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

        self.pipeline_play.set_state(gst.STATE_PLAYING)

        if self.channel:
            print 'before: ', self.source.get_channel().label
            chan = self.source.find_channel_by_name(self.channel)
            self.source.set_channel(chan)
            print 'after: ', self.source.get_channel().label
    
        if self.norm:
            norm = self.source.find_norm_by_name(self.norm)
            self.source.set_norm(norm)

        self.pipeline_play.set_state(gst.STATE_PLAYING)
        print 'long after: ',self.source.get_channel().label

        return True
                    
    def pipeline_start(self):
        self.pipeline_play.set_state(gst.STATE_PLAYING)

    def pipeline_destroy(self):
        self.pipeline_play.set_state(gst.STATE_NULL)

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
        self.counter += 1
        if self.counter == 10:
            gc.collect()
            self.counter = 0
                                             
        return True 
          
    def input_combo_change(self, combo):
        option = combo.get_active()

        widget = self.xml.get_widget('hboxBttv')
        widget.props.visible = False
        
        widget = self.xml.get_widget('vboxWebcam')
        widget.props.visible = False

        if option == 0:
            # bttv selected
            box = self.xml.get_widget('hboxBttv')
            box.props.visible = True
        elif option == 1:
            # webcam selected
            box = self.xml.get_widget('vboxWebcam')
            box.props.visible = True            
        elif option == 2:
            # firewire selected
            print 'not implemented yet'
    
    def set_combo_width(self, input_option, combo):
        model = gtk.ListStore(gobject.TYPE_INT)
        input_type = input_option.get_active()
        if input_type == 0:
            # bttv selected
            model.append( [640] )
        model.append( [320] )
        model.append( [160] )

        itr = None
        for item in model:
            if item[0] == self.width:
                itr = item.iter
                break

        combo.set_model(model)
        if itr:
            combo.set_active_iter(itr)
    
    def combo_width_change(self, combo):
        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.width = value
        self.set_default_pipeline_string(None)

    def combo_height_change(self, combo):
        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.height = value
        self.set_default_pipeline_string(None)

    def set_combo_height(self, input_option, combo):
        model = gtk.ListStore(gobject.TYPE_INT)
        input_type = input_option.get_active()
        if input_type == 0:
            # bttv selected
            model.append( [480] )
        model.append( [240] )
        model.append( [120] )

        itr = None
        for item in model:
            if item[0] == self.height:
                itr = item.iter
                break

        combo.set_model(model)
        if itr:
            combo.set_active_iter(itr)

    def combo_device_change(self, combo):
        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.device = str(value)
        self.set_default_pipeline_string(None)

    def set_combo_device(self, input_type, combo):
        model = gtk.ListStore(gobject.TYPE_STRING)
        # TODO: how to verify if a device exists?
        model.append( ['/dev/video0'] )
        model.append( ['/dev/video1'] )
        model.append( ['/dev/video2'] )

        itr = None
        for item in model:
            if item[0] == self.device:
                itr = item.iter
                break

        combo.set_model(model)
        if itr:
            combo.set_active_iter(itr)

        combo.set_model(model)

    def combo_channel_change(self, combo):
        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.channel = str(value)

    def combo_norm_change(self, combo):
        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.norm = str(value)

    def set_combo_channel(self, input_type, combo):
        if input_type.get_active() == 0:
            # bttv selected
            try:
                channels = [chan.label for chan in self.source.list_channels()]
            except:
                print "device doesn't support channels"
            else:
                model = gtk.ListStore(gobject.TYPE_STRING)
                for item in channels:
                    model.append([item])
                combo.set_model(model)            

    def set_combo_norm(self, input_type, combo):
        if input_type.get_active() == 0:
            # bttv selected
            try:
                norms = [norm.label for norm in self.source.list_norms()]
            except:
                print "device doesn't support norm"
            else:
                model = gtk.ListStore(gobject.TYPE_STRING)
                for item in norms:
                    model.append([item])
                combo.set_model(model)            

    def show_window(self, button):
        self.devicewindow.show_all()        

        widget = self.xml.get_widget('hboxBttv')
        widget.props.visible = False
        
        widget = self.xml.get_widget('vboxWebcam')
        widget.props.visible = False

        height = self.xml.get_widget('comboboxHeight')
        width = self.xml.get_widget('comboboxWidth')

        self.xml.get_widget('notebookDeviceManager').set_current_page(0)

        self.xml.get_widget('comboboxInputType').emit('changed')

        response = self.devicewindow.run()
        if response == gtk.RESPONSE_OK :

            temp = width.get_active_iter()
            value = width.get_model().get_value(temp, 0)
            self.width = value

            temp = height.get_active_iter()
            value = height.get_model().get_value(temp, 0)
            self.height = value

#            self.set_default_pipeline_string(None)
            self.set_pipelines()
            self.devicewindow.hide_all()
        else:
            self.devicewindow.hide_all()
        
    def delete(self, widget, event):
        self.devicewindow.hide_all()
        
