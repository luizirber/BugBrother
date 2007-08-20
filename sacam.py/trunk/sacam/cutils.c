#include <Python.h>
#include "structmember.h"

#include <pygobject.h>
#include <pygtk/pygtk.h>

#include <glib.h>
#include <glib/gprintf.h>

#include <gdk/gdkpixbuf.h>

#include <time.h>

static PyTypeObject *PyGObject_Type=NULL;

/*static GdkPixbuf*
__new_from_pixbuf(guchar *data, GdkColorspace colorspace, gboolean has_alpha,
                int bits_per_sample, int width, int height, int rowstride)
{
    int row, column, pos;
    guint32 pixel;
    for (row = 0; row < height; row++) {
        for (column = 0; column < width; column++) {
            pos = row*rowstride + column*bits_per_sample;
            pixel = data[pos];
            data[pos] =(
                        (pixel <<  8 & 0xffffff00) |
                        (pixel >> 24 & 0x000000ff)
                       );
        }
    }
    return gdk_pixbuf_new_from_data (data, colorspace, has_alpha,
                      bits_per_sample, width, height, rowstride, NULL, NULL);
}
*/
static PyGObject*
cutils_convert_ARGB_to_RGBA (PyObject* self, PyObject* args)
{
    PyGObject* old_pixbuf;

    if ( !PyArg_ParseTuple(args, "O!", PyGObject_Type, &old_pixbuf) )
        return NULL;

    int row, column;
    int rowstride = gdk_pixbuf_get_rowstride(GDK_PIXBUF(old_pixbuf->obj));
    int nchannels = gdk_pixbuf_get_n_channels(GDK_PIXBUF(old_pixbuf->obj));
    int height = gdk_pixbuf_get_height(GDK_PIXBUF(old_pixbuf->obj));
    int width = gdk_pixbuf_get_width(GDK_PIXBUF(old_pixbuf->obj));
    guchar* pixels = gdk_pixbuf_get_pixels(GDK_PIXBUF(old_pixbuf->obj));
    guchar* current;

    for (row = 0; row < height; row++) {
        for (column = 0; column < width; column++) {
            current = pixels + row*rowstride + column*nchannels;
            guchar aux = current[0]; // Save the value of Alpha component
            current[0] = current[1]; // Put value of R in the right position
            current[1] = current[2]; // Same with G
            current[2] = current[3]; // Same with B
            current[3] = aux;        // Put the Alpha value in right place
        }
    }

    return Py_BuildValue("O", old_pixbuf);

}

static PyObject*
cutils_tortuosity(PyObject* self, PyObject* args)
{
    PyObject* point_list, *curr_point, *aux_point, *aux_obj;
    double tort = 0,
           max_distance = 0,
           distance = 0,
           lenght = 0,
           precision = 0.01;
    int size, i, j;
    long int curr_xpos, curr_ypos, xpos, ypos, prev_xpos = 0, prev_ypos = 0;

    if (!PyArg_ParseTuple(args, "O", &point_list))
        return NULL;

    size = PyList_Size(point_list);
    if (size <= 1)
        return Py_BuildValue("d", 0);

    for (i = 0; i < size; i++) {
        curr_point = PyList_GetItem(point_list, i);

        aux_obj = PyObject_GetAttrString(curr_point, "x_pos");
        curr_xpos = PyInt_AsLong(aux_obj);
        Py_DECREF(aux_obj);

        aux_obj = PyObject_GetAttrString(curr_point, "y_pos");
        curr_ypos = PyInt_AsLong(aux_obj);
        Py_DECREF(aux_obj);

        for (j = 0; j < size; j++) {
            aux_point = PyList_GetItem(point_list, j);

            aux_obj = PyObject_GetAttrString(aux_point, "x_pos");
            xpos = PyInt_AsLong(aux_obj);
            Py_DECREF(aux_obj);

            aux_obj = PyObject_GetAttrString(aux_point, "y_pos");
            ypos = PyInt_AsLong(aux_obj);
            Py_DECREF(aux_obj);

            distance = sqrt( pow(curr_xpos - xpos, 2) +
                             pow(curr_ypos - ypos, 2));
            if (distance > max_distance)
                max_distance = distance;
        }

        if (i) {
            lenght += sqrt( pow(curr_xpos - prev_xpos, 2) +
                            pow(curr_ypos - prev_ypos, 2) );
        }
        prev_xpos = curr_xpos;
        prev_ypos = curr_ypos;
    }

    if (lenght == 0)
        tort = 0;
    else
        tort = 1 - (max_distance/lenght);

    if (tort < precision)
        tort = 0;

    return Py_BuildValue("d", tort);
}

static PyMethodDef module_methods[] = {
    {"tortuosity", cutils_tortuosity, METH_VARARGS,
     "Calculate the tortuosity of a track"},
    {"convert", cutils_convert_ARGB_to_RGBA, METH_VARARGS,
     "Convert a ARGB pixbuf to a RGBA pixbuf"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcutils(void)
{
    PyObject* m;
    PyObject* module;

    m = Py_InitModule3("cutils", module_methods,
                       "Utility functions in C");

    if (m == NULL)
        return;

    init_pygobject();
    init_pygtk();
    module = PyImport_ImportModule("gobject");
    if (module) {
        PyGObject_Type = (PyTypeObject*)PyObject_GetAttrString(module, "GObject");
        Py_DECREF(module);
    }
}
