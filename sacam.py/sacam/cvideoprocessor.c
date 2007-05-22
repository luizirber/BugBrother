#include <Python.h>
#include "structmember.h"
#include "datetime.h"

#include <pygobject.h>
#include <pygtk/pygtk.h>

#include <glib.h>
#include <glib/gprintf.h>
#include <gdk/gdkpixbuf.h>

#include <time.h>

static PyTypeObject *PyGObject_Type=NULL;
static PyTypeObject *PyObject_PointType=NULL;

typedef struct {
    PyObject_HEAD
    PyGObject *previous;
    PyGObject *current;
    PyObject  *window;
    guint32 threshold;
    GdkGC* gc;
    gboolean first_run;
    gboolean window_is_defined;
    gchar initial;
    gchar final;
    gdouble bug_size;
    guint middle_height;
    guint middle_width;
} Videoprocessor;

static void
Videoprocessor_dealloc(Videoprocessor* self)
{
    Py_XDECREF(self->previous);
    Py_XDECREF(self->current);
    Py_XDECREF(self->window);
    g_free(self->gc);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Videoprocessor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    g_type_init();
    Videoprocessor *self;
    self = (Videoprocessor *)type->tp_alloc(type, 0);
    if (self != NULL) {

        GdkPixbuf *pixbuf;
        pixbuf = gdk_pixbuf_new(GDK_COLORSPACE_RGB,
                                 FALSE, 8, 10, 10);
        self->previous = pygobject_new((GObject *) pixbuf);
        if (self->previous == NULL) {
            Py_DECREF(self);
            return NULL;
        }

        pixbuf = gdk_pixbuf_new(GDK_COLORSPACE_RGB,
                                 FALSE, 8, 10, 10);
        self->current = pygobject_new((GObject *) pixbuf);
        if (self->current == NULL) {
            Py_DECREF(self);
            return NULL;
        }

        Py_XINCREF(self->window);

    }

    return (PyObject *)self;
}

static int
Videoprocessor_init(Videoprocessor *self, PyObject *args, PyObject *kwds)      
{
    self->first_run = TRUE;
    self->window_is_defined = FALSE;    
    return 0;
}

static PyMemberDef Videoprocessor_members[] = {
    {NULL}  /* Sentinel */
};

static PyGObject *
Videoprocessor_getprevious(Videoprocessor *self, void *closure)
{
    Py_INCREF(self->previous);
    return self->previous;
}

static int
Videoprocessor_setprevious(Videoprocessor *self, PyGObject *value, void *closure)
{
    if (GDK_IS_PIXBUF(value->obj)) {
        Py_XDECREF(self->previous);
        self->previous = pygobject_new((GObject*)value->obj);
    }
    else {
        PyErr_SetString(PyExc_TypeError, 
                    "The 'previous' attribute value must be a gtk.gdk.pixbuf");
        return -1;
    }

    return 0;
}

static PyGObject *
Videoprocessor_getcurrent(Videoprocessor *self, void *closure)
{
    Py_INCREF(self->current);
    return self->current;
}

static int
Videoprocessor_setcurrent(Videoprocessor *self, PyGObject *value, void *closure)
{
    if (GDK_IS_PIXBUF(value->obj)) {
        Py_XDECREF(self->current);
        self->current = pygobject_new((GObject*)value->obj);
    }
    else {
        PyErr_SetString(PyExc_TypeError, 
                    "The 'current' attribute value must be a gtk.gdk.pixbuf");
        return -1;
    }

    return 0;
}

static PyGetSetDef Videoprocessor_getsetters[] = {
    {"previous", 
     (getter)Videoprocessor_getprevious, (setter)Videoprocessor_setprevious,
     "previous pixbuf",
     NULL},
    {"current", 
     (getter)Videoprocessor_getcurrent, (setter)Videoprocessor_setcurrent,
     "current pixbuf",
     NULL},
    {NULL}
};

static PyObject *
Videoprocessor_process_video(Videoprocessor* self, PyObject *args)
{
    PyGObject *source;
    PyGObject *output;
    PyObject *project;
    PyObject *current_experiment;    
    
    if (!PyArg_ParseTuple(args, "O!O!O", PyGObject_Type, &source,
                                         PyGObject_Type, &output, 
                                         &project))
        return NULL;

    current_experiment = PyObject_GetAttrString(project, 
                                            "current_experiment");
    
    PyObject *datetime_obj = PyDateTime_FromDateAndTime(1,1,1,1,1,1,1);

    if (self->first_run == TRUE) {

        PyObject *threshold;
        PyObject *initial;
        PyObject *final;
        PyObject *bug_size;
        PyObject *bug_max_speed;
        
        PyObject *now;
        now = PyObject_CallMethod(datetime_obj, "now", NULL);
        PyObject_SetAttrString(current_experiment, "start_time", now);
        Py_XDECREF(now);

        threshold = PyObject_GetAttrString(current_experiment,
                                           "threshold");
        self->threshold = ( PyInt_AsLong(threshold) << 24 |
                            PyInt_AsLong(threshold) << 16 |
                            PyInt_AsLong(threshold) <<  8 
                          );        

        self->window = PyObject_GetAttrString(current_experiment,
                                              "release_area");

        initial = PyList_GetItem(self->window, 2);
        final = PyList_GetItem(self->window, 0);
        self->middle_height = (PyInt_AsLong(initial) + PyInt_AsLong(final))/2;

        initial = PyList_GetItem(self->window, 3);
        final = PyList_GetItem(self->window, 1);
        self->middle_width = (PyInt_AsLong(initial) + PyInt_AsLong(final))/2;
        
        bug_size = PyObject_GetAttrString(project, "bug_size");
        bug_max_speed = PyObject_GetAttrString(project, "bug_max_speed");
        self->bug_size = PyFloat_AsDouble(bug_size) + PyFloat_AsDouble(bug_max_speed);

        self->gc = gdk_gc_new(GTK_WIDGET(output->obj)->window);
        gdk_gc_set_line_attributes (self->gc, 5, GDK_LINE_ON_OFF_DASH,
                                    GDK_CAP_NOT_LAST, GDK_JOIN_MITER);

        Py_XDECREF(threshold); 
        Py_XDECREF(bug_size);
        Py_XDECREF(bug_max_speed);

        Videoprocessor_setcurrent(self, source, NULL);
        Videoprocessor_setprevious(self, source, NULL);
        self->first_run = FALSE;

        Py_RETURN_TRUE;        
    }   
    else {
        Videoprocessor_setprevious(self, self->current, NULL);          
        Videoprocessor_setcurrent(self, source, NULL);

        PyObject *begin, *end;
        PyObject *initial, *final;
        gdouble size;
        gint rows_start, rows_finish;
        gint pixels_start, pixels_finish;
        
        begin = PyObject_CallMethod(datetime_obj, "now", NULL);

        initial = PyList_GetItem(self->window, 2);
        final = PyList_GetItem(self->window, 0);
        size = (PyInt_AsLong(initial) - PyInt_AsLong(final))/2;
        if (size < self->bug_size)
            size = self->bug_size;
        rows_start = self->middle_height - (gint)size;
        if (rows_start < 0)
            rows_start = 0;
        rows_finish = self->middle_height + (gint)size;
        if (rows_finish > gdk_pixbuf_get_height (GDK_PIXBUF(self->current->obj)) )
            rows_finish = gdk_pixbuf_get_height (GDK_PIXBUF(self->current->obj));

        initial = PyList_GetItem(self->window, 3);
        final = PyList_GetItem(self->window, 1);
        size = (PyInt_AsLong(initial) - PyInt_AsLong(final))/2;
        if (size < self->bug_size)
            size = self->bug_size;
        pixels_start = self->middle_width - (gint)size;
        if (pixels_start < 0)
            pixels_start = 0;
        pixels_finish = self->middle_width + (gint)size;
        if (pixels_finish > gdk_pixbuf_get_width (GDK_PIXBUF(self->current->obj)) )
            pixels_finish = gdk_pixbuf_get_width (GDK_PIXBUF(self->current->obj));

        self->window_is_defined = FALSE;

        gint row, pixel;
        for (row = rows_start; row < rows_finish; row++) {
            for (pixel = pixels_start; pixel < pixels_finish; pixel++) {

                guint n_channels, rowstride;
    
                guchar *pixels, 
                       *current,
                       *previous;
    
                pixels = gdk_pixbuf_get_pixels (GDK_PIXBUF(self->current->obj));
                n_channels = gdk_pixbuf_get_n_channels (GDK_PIXBUF(self->current->obj));
                rowstride = gdk_pixbuf_get_rowstride (GDK_PIXBUF(self->current->obj));
                current = pixels + pixel * n_channels + row * rowstride;

                pixels = gdk_pixbuf_get_pixels (GDK_PIXBUF(self->previous->obj));
                n_channels = gdk_pixbuf_get_n_channels (GDK_PIXBUF(self->previous->obj));
                rowstride = gdk_pixbuf_get_rowstride (GDK_PIXBUF(self->previous->obj));
                previous = pixels + pixel * n_channels + row * rowstride;
                
                guint32 pixel_previous;
                guint32 pixel_current;

                pixel_previous = (
                                   (previous[0]) << 24 | 
                                   (previous[1]) << 16 |
                                   (previous[2]) <<  8
                                );            

                pixel_current = (
                                  (current[0]) << 24 | 
                                  (current[1]) << 16 |
                                  (current[2]) <<  8 
                                );

                guint32 max, min;
                if (pixel_previous > self->threshold)
                    min = (pixel_previous - self->threshold);                    
                else
                    min = 0;

                if (pixel_previous > (0xffffff00 - self->threshold) )
                    max = 0xffffff00;
                else
                    max = (pixel_previous + self->threshold);

                if ( (pixel_current < min ) || (pixel_current > max ) ) {
                    if (self->window_is_defined == TRUE) {
                        PyObject *row_temp, *pixel_temp;
                        row_temp = Py_BuildValue("i", row);
                        pixel_temp = Py_BuildValue("i", pixel);
                        PyList_SetItem(self->window, 2, row_temp);
                        PyList_SetItem(self->window, 3, pixel_temp);                       
                    }
                    else {
                        PyObject *row_temp, *pixel_temp;
                        row_temp = Py_BuildValue("i", row);
                        Py_XINCREF(row_temp);
                        pixel_temp = Py_BuildValue("i", pixel);
                        Py_XINCREF(pixel_temp);
                        PyList_SetItem(self->window, 0, row_temp);
                        PyList_SetItem(self->window, 1, pixel_temp);
                        PyList_SetItem(self->window, 2, row_temp);
                        PyList_SetItem(self->window, 3, pixel_temp);
                        self->window_is_defined = TRUE;
                    }
                }

                while (gtk_events_pending ())
                    gtk_main_iteration ();
            }
        }
        

        end = PyObject_CallMethod(datetime_obj, "now", NULL);

        initial = PyList_GetItem(self->window, 3);
        final = PyList_GetItem(self->window, 1);
        self->middle_width = (PyInt_AsLong(initial) + PyInt_AsLong(final))/2;
        
        initial = PyList_GetItem(self->window, 2);
        final = PyList_GetItem(self->window, 0);
        self->middle_height = (PyInt_AsLong(initial) + PyInt_AsLong(final))/2;

        gdk_draw_pixbuf (GTK_WIDGET(output->obj)->window, 
                         self->gc,
                         GDK_PIXBUF(self->current->obj),
                         0, 0,
                         0, 0,
                         -1, -1,
                         GDK_RGB_DITHER_NONE, 0, 0);
    
        gdk_draw_rectangle (GTK_WIDGET(output->obj)->window, //output
                            self->gc,                        //GC
                            FALSE,                           //filled?
                            pixels_start, rows_start,        //(x0, y0)
                            pixels_finish - pixels_start,    //width
                            rows_finish - rows_start);       //height
    
        gint w_initial, w_final;
        gint h_initial, h_final;

        w_initial = PyInt_AsLong (PyList_GetItem (self->window, 1));
        w_final   = PyInt_AsLong (PyList_GetItem (self->window, 3));
        h_initial = PyInt_AsLong (PyList_GetItem (self->window, 0));
        h_final   = PyInt_AsLong (PyList_GetItem (self->window, 2));

        gdk_draw_rectangle (GTK_WIDGET(output->obj)->window, //output
                            self->gc,                        //GC
                            FALSE,                           //filled?
                            w_initial, h_initial,            //(x0,y0) 
                            w_final - w_initial,             //width
                            h_final - h_initial);            //height

        gdk_draw_rectangle (GTK_WIDGET(output->obj)->window, //output
                            self->gc,                        //GC
                            TRUE,                            //filled?
                            self->middle_width - 3,          //x0 
                            self->middle_height - 3,         //y0
                            6, 6);                           //height

        PyObject* ptemp;
        PyObject* value;
        PyObject* point_list;

        ptemp = PyObject_CallObject(PyObject_PointType, NULL);

        value = Py_BuildValue("i", self->middle_width);
        PyObject_SetAttrString(ptemp, "x_pos", value);
        Py_XDECREF(value);

        value = Py_BuildValue("i", self->middle_height);
        PyObject_SetAttrString(ptemp, "y_pos", value);
        Py_XDECREF(value);

        PyObject_SetAttrString(ptemp, "start_time", begin);
        PyObject_SetAttrString(ptemp, "end_time", end);

        current_experiment = PyObject_GetAttrString(project,
                                                "current_experiment");

        point_list = PyObject_GetAttrString(current_experiment,
                                            "point_list");
        PyList_Append(point_list, ptemp);

        Py_XDECREF(point_list);
        Py_XDECREF(ptemp);

        Py_XDECREF(begin);
        Py_XDECREF(end);
    }

//    Py_XDECREF(datetime_obj);
//    Py_XDECREF(current_experiment);
    Py_RETURN_TRUE;
}

static PyMethodDef Videoprocessor_methods[] = {
    {"process_video", (PyCFunction)Videoprocessor_process_video, METH_VARARGS,
     "Apply the detection algorithm in the video input"
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject VideoprocessorType = {
    PyObject_HEAD_INIT(NULL)
    0,                                           /* ob_size */
    "cvideoprocessor.Videoprocessor",            /* tp_name */
    sizeof(Videoprocessor),                      /* tp_basicsize */
    0,                                           /* tp_itemsize */
    (destructor)Videoprocessor_dealloc,          /* tp_dealloc */
    0,                                           /* tp_print */
    0,                                           /* tp_getattr */
    0,                                           /* tp_setattr */
    0,                                           /* tp_compare */
    0,                                           /* tp_repr */
    0,                                           /* tp_as_number */
    0,                                           /* tp_as_sequence */
    0,                                           /* tp_as_mapping */
    0,                                           /* tp_hash */
    0,                                           /* tp_call */
    0,                                           /* tp_str */
    0,                                           /* tp_getattro */
    0,                                           /* tp_setattro */
    0,                                           /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,    /* tp_flags*/
    "Videoprocessor object",                     /* tp_doc */
    0,                                           /* tp_traverse */
    0,                                           /* tp_clear */
    0,                                           /* tp_richcompare */
    0,                                           /* tp_weaklistoffset */
    0,                                           /* tp_iter */
    0,                                           /* tp_iternext */
    Videoprocessor_methods,                      /* tp_methods */
    Videoprocessor_members,                      /* tp_members */
    Videoprocessor_getsetters,                   /* tp_getset */
    0,                                           /* tp_base */
    0,                                           /* tp_dict */
    0,                                           /* tp_descr_get */
    0,                                           /* tp_descr_set */
    0,                                           /* tp_dictoffset */
    (initproc)Videoprocessor_init,               /* tp_init */
    0,                                           /* tp_alloc */
    Videoprocessor_new,                          /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initvideoprocessor(void)
{
    PyObject* m;
    PyObject* module;

    if (PyType_Ready(&VideoprocessorType) < 0)
        return;

    m = Py_InitModule3("cvideoprocessor", module_methods,
                       "Module used in video processing.");

    if (m == NULL)
        return;

    Py_INCREF(&VideoprocessorType);
    PyModule_AddObject(m, "Videoprocessor",
                       (PyObject *)&VideoprocessorType);

    PyDateTime_IMPORT;

    init_pygobject();
    init_pygtk();
    module = PyImport_ImportModule("gobject");
    if (module) {
        PyGObject_Type = (PyTypeObject*)PyObject_GetAttrString(module, "GObject");
        Py_DECREF(module);
    }

    module = PyImport_ImportModule("areas");
    if (module) {
        PyObject_PointType = (PyTypeObject*)PyObject_GetAttrString(module, "Point");
        Py_DECREF(module);
    }
}
