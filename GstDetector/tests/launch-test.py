import gst
import gtk

sink = None
detector = None

def expose_cb(area, event):
    global sink
    sink.set_xwindow_id(area.window.xid)

def clicked_cb(output, event):
    x0, y0 = event.x - 25, event.y - 25
    x1, y1 = event.x + 25, event.y + 25
    if x0 < 0: x0 = 0
    if x1 < 0: x1 = 0
    if y0 < 0: y0 = 0
    if y1 < 0: y1 = 0
    detector.props.tracking_area = [x0, y0, x1, y1]

def run():
    global sink
    global detector
    pipeline_string = "v4lsrc name=source ! ffmpegcolorspace ! " \
                      "video/x-raw-rgb,width=640,height=480 ! " \
                      "motiondetector name=tracker active=true " \
                      "draw-boxes=true draw-track=true size=50 silent=true " \
                      "threshold=100 ! ximagesink name=sink"

    pipeline = gst.parse_launch(pipeline_string)
    pipeline.set_state(gst.STATE_PAUSED)

    source = pipeline.get_by_name("source")
    sink = pipeline.get_by_name("sink")
    detector = pipeline.get_by_name("tracker")
    detector.props.tracking_area = [50,50,70,70]
    #chan = source.find_channel_by_name("Composite1")
    source.set_norm(source.list_norms()[1])
    source.set_channel(source.list_channels()[1])

    pipeline.set_state(gst.STATE_PLAYING) 

def main():
    w = gtk.Window()
    b = gtk.HBox()
    d = gtk.DrawingArea()
    b.pack_start(d)
    w.add(b)

    run() 

    w.show_all()

    d.connect("expose-event", expose_cb)
    d.add_events(  gtk.gdk.BUTTON_PRESS_MASK 
                      | gtk.gdk.BUTTON_RELEASE_MASK
                      | gtk.gdk.BUTTON_MOTION_MASK
                      | gtk.gdk.KEY_PRESS_MASK
                      | gtk.gdk.KEY_RELEASE_MASK   )
    d.connect("button-press-event", clicked_cb)

    gtk.main()

if __name__ == "__main__":
    main()
