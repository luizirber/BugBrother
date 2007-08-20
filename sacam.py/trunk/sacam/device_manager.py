''' This module contains the DeviceManager class, which does the interfacing
    with GStreamer. '''

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

import pygst
pygst.require('0.10')
import gst

from kiwi.environ import environ

from sacam.gstvideoprocessor import Videoprocessor
from sacam.cutils import convert
from sacam.i18n import APP_NAME

class DeviceManager(object):
    ''' Encapsulate the GStreamer funcionality and the videoprocessor. '''

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

    def __init__(self, video_output):

        gladefile = environ.find_resource('glade', 'sacam.glade')
        windowname = "devicemanager"
        self.xml = gtk.glade.XML(gladefile, windowname, domain=APP_NAME)
        self.devicewindow = self.xml.get_widget(windowname)
        self.devicewindow.connect("delete-event", self.delete)

        self.outputarea = video_output
        self.processor = Videoprocessor("motiondetector")
        self.processor.output = video_output
#        self.processor = Videoprocessor("identity")
        self.outputarea.connect("expose-event", self.expose_cb)
        self.outputarea.add_events(  gtk.gdk.BUTTON_PRESS_MASK
                                   | gtk.gdk.BUTTON_RELEASE_MASK
                                   | gtk.gdk.BUTTON_MOTION_MASK
                                   | gtk.gdk.KEY_PRESS_MASK
                                   | gtk.gdk.KEY_RELEASE_MASK )
        self.outputarea.connect("button-press-event", self.position_change)

        self.device = '/dev/video0'
        self.width, self.height = 320, 240
        self.outputarea.set_size_request(self.width, self.height)
        self.norm, self.channel = None, None

        self.pipeline_string = ''
        self.null = None
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
            print 'error!' #TODO

    def position_change(self, widget, event):
        self.processor.set_new_tracking_area(event.x, event.y)

    def connect_processor_props(self, xml):
        #draw property
        prop = xml.get_widget("checkbuttonMask")
        prop.set_active(self.processor.detector.props.draw & (1))
        prop.connect("toggled", self.set_draw_methods, "mask")

        prop = xml.get_widget("checkbuttonTrack")
        prop.set_active(self.processor.detector.props.draw & (1 << 1))
        prop.connect("toggled", self.set_draw_methods, "track")

        prop = xml.get_widget("checkbuttonBox")
        prop.set_active(self.processor.detector.props.draw & (1 << 2))
        prop.connect("toggled", self.set_draw_methods, "box")

        #size property
        prop = xml.get_widget("scaleSize")
        prop.set_range(0, min(self.frame["height"], self.frame["width"]))
        prop.set_value(self.processor.detector.props.size)
        prop.connect("value-changed", self.set_scale, "size")

        #speed property
        prop = xml.get_widget("scaleSpeed")
        prop.set_range(0, min(self.frame["height"], self.frame["width"]))
        prop.set_value(self.processor.detector.props.speed)
        prop.connect("value-changed", self.set_scale, "speed")

        #threshold property
        prop = xml.get_widget("scaleThreshold")
        prop.set_value(self.processor.detector.props.threshold)
        prop.connect("value-changed", self.set_scale, "threshold")

        #tolerance property
        prop = xml.get_widget("scaleTolerance")
        prop.set_range(0, min(self.frame["height"], self.frame["width"]))
        prop.set_value(self.processor.detector.props.tolerance)
        prop.connect("value-changed", self.set_scale, "tolerance")

    def set_draw_methods(self, button, type):
        self.processor.draw[type] = button.get_active()

        self.processor.detector.props.draw = self.processor.draw["mask"] \
                                        | self.processor.draw["track"] << 1 \
                                        | self.processor.draw["box"]   << 2

    def set_scale(self, scale, prop):
        self.processor.set_property(prop, int(scale.get_value()))

    def set_default_pipeline_string(self, button):
        ''' Set the default pipeline string, using the v4lsrc element. '''

        pipeline_string = (
           'v4lsrc device=%s name=source ! ffmpegcolorspace ! '
           'video/x-raw-rgb,format=ARGB,width=%d,height=%d ! '
           '%s name=motionfilter ! '
           )%(self.device, self.width, self.height,
              self.processor.get_detector_name())

        self.pipeline_string = pipeline_string
        self.textview.get_buffer().set_text(pipeline_string)

    def set_testing_pipeline_string(self, button):
        ''' Set the testing pipeline string, using the videotestsrc element. '''

        pipeline_string = (
            'videotestsrc name=source ! ffmpegcolorspace ! '
            'video/x-raw-rgb,format=ARGB,width=%d,height=%d ! '
            '%s name=motionfilter ! '
           )%(self.width, self.height, self.processor.get_detector_name())

        self.pipeline_string = pipeline_string
        self.textview.get_buffer().set_text(pipeline_string)

    def set_pipelines(self):
        ''' Based on the current pipeline_string this function builds the
            new pipeline, after verifying if it is valid. '''

        fake_sink = 'fakesink'
        if sys.platform == "win32":
            video_sink = 'directdrawsink name=sink keep-aspect-ratio=true'
        else:
#            video_sink = 'ffmpegcolorspace ! xvimagesink name=sink'
            video_sink = 'ximagesink name=sink force-aspect-ratio=true'
#        video_sink = 'autovideosink'
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

        motionfilter = pipeline.get_by_name("motionfilter")
        self.processor.set_detector(motionfilter)
        motionfilter.connect("handoff", self.frame_setter)
        self.sink = self.pipeline_play.get_by_name("sink")

        bus = pipeline.get_bus()
        bus.add_signal_watch()

        self.pipeline_play.set_state(gst.STATE_PAUSED)

        if self.channel:
            chan = self.source.find_channel_by_name(self.channel)
            self.source.set_channel(chan)

        if self.norm:
            norm = self.source.find_norm_by_name(self.norm)
            self.source.set_norm(norm)

        self.outputarea.set_size_request(self.width, self.height)

        self.pipeline_play.set_state(gst.STATE_PLAYING)

        return True

    def pipeline_start(self):
        ''' Start the current pipeline '''

        self.pipeline_play.set_state(gst.STATE_PLAYING)

    def pipeline_destroy(self):
        ''' Put the current pipeline in a NULL state, meaning that it can be
            destroyed. '''

        self.pipeline_play.set_state(gst.STATE_NULL)

    def expose_cb(self, wid, event):
        ''' Callback function executed every time the outputarea is exposed. 

            Needed to put the GStreamer sink on the outputarea. '''
        self.outputarea.set_size_request(self.frame['width'],
                                         self.frame['height'])
        if sys.platform == 'win32':
            self.sink.set_xwindow_id(self.outputarea.window.handle)
        else:
            self.sink.set_xwindow_id(self.outputarea.window.xid)

    def frame_setter(self, element, buf):
        ''' Every time a new buffer is sent accross the pipeline its data
            is stored to be used afterwards. '''

        for structure in buf.caps:
            if structure["format"] == "ARGB":
                self.frame = structure
                self.frame_buf = buf.data
            if structure["format"] == "YUV2":
                #TODO: implement colorspace conversion?
                pass

    def get_current_frame(self):
        ''' Return a pixbuf from the current buffer. '''
        pbuf = gtk.gdk.pixbuf_new_from_data(self.frame_buf,
                   gtk.gdk.COLORSPACE_RGB, True, 8,
                   self.frame["width"], self.frame["height"],
                   self.frame["width"]*4)
        if self.frame["format"] == "ARGB":
            return convert(pbuf)
        return pbuf

    def start_video(self, project, wait_click=False):
        ''' Start the video processing of the input. '''

        self.processor.start(self.frame, project)

    def stop_video(self, project):
        self.processor.stop(project)

    def input_combo_change(self, combo):
        ''' Update the input type combo, showing the extra properties. '''

        option = combo.get_active()

        widget = self.xml.get_widget('hboxBttv')
        widget.props.visible = False

#        widget = self.xml.get_widget('vboxWebcam')
#        widget.props.visible = False

        if option == 0:
            # bttv selected
            box = self.xml.get_widget('hboxBttv')
            box.props.visible = True
        elif option == 1:
            # webcam selected
            pass
#            box = self.xml.get_widget('vboxWebcam')
#            box.props.visible = True
        elif option == 2:
            # firewire selected
            print 'not implemented yet'

    def set_combo_width(self, input_option, combo):
        ''' Update the width of the video based on the input type '''

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
        ''' Set the video width based on the current combo value. '''

        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.width = value
        self.set_default_pipeline_string(None)

    def combo_height_change(self, combo):
        ''' Set the video height based on the current combo value. '''

        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.height = value
        self.set_default_pipeline_string(None)

    def set_combo_height(self, input_option, combo):
        ''' Update the height of the video based on the input type '''

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
        ''' Set the video device based '''

        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.device = str(value)
        self.set_default_pipeline_string(None)

    def set_combo_device(self, input_type, combo):
        ''' Update the video device based on the input type '''

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
        ''' Set the video device channel based on the combo value'''

        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.channel = str(value)

    def combo_norm_change(self, combo):
        ''' Set the video device norm based on the combo value'''

        temp = combo.get_active_iter()
        value = combo.get_model().get_value(temp, 0)
        self.norm = str(value)

    def set_combo_channel(self, input_type, combo):
        ''' Update the video device channel based on the current video device'''

        if input_type.get_active() == 0:
            # bttv selected
            try:
                channels = [chan.label for chan in self.source.list_channels()]
            except AttributeError:
                print "device doesn't support channels"
            else:
                model = gtk.ListStore(gobject.TYPE_STRING)
                for item in channels:
                    model.append([item])
                combo.set_model(model)

    def set_combo_norm(self, input_type, combo):
        ''' Update the video device norm based on the current video device'''

        if input_type.get_active() == 0:
            # bttv selected
            try:
                norms = [norm.label for norm in self.source.list_norms()]
            except AttributeError:
                print "device doesn't support norm"
            else:
                model = gtk.ListStore(gobject.TYPE_STRING)
                for item in norms:
                    model.append([item])
                combo.set_model(model)

    def show_window(self, button):
        ''' Show the DeviceManager dialog, and set the appropriate behavior
            of its widgets. '''

        self.devicewindow.show_all()

        widget = self.xml.get_widget('hboxBttv')
        widget.props.visible = False

#        widget = self.xml.get_widget('vboxWebcam')
#        widget.props.visible = False

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
        ''' Hide the dialog, instead of destroy it. '''
        self.devicewindow.hide_all()

