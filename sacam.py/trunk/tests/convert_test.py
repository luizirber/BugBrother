from sacam.cutils import convert
import gtk.gdk

def get_pixbuf():
    return gtk.gdk.pixbuf_new_from_file("input.jpg")

if __name__ == "__main__":
    new_pixbuf = convert(get_pixbuf())
    new_pixbuf.save("output.jpg", "jpeg", {"quality":100})
