#include <Python.h>
#include "structmember.h"

#include <glib.h>
#include <gdk/gdkpixbuf.h>

typedef struct {
    PyObject_HEAD
    GdkPixbuf* first;
    GdkPixbuf* previous;
    GdkPixbuf* current;
    GTimer* timer;
    guint32 threshold;
} Videoprocessor;

static void
Videoprocessor_dealloc(Videoprocessor* self)
{
    g_object_unref(self->first);
    g_object_unref(self->previous);
    g_object_unref(self->current);
    g_object_unref(self->timer);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Videoprocessor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    g_type_init();    
    Videoprocessor *self;
    self = (Videoprocessor *)type->tp_alloc(type, 0);
    if (self != NULL) {

        self->first = gdk_pixbuf_new(GDK_COLORSPACE_RGB,
                                      FALSE, 8, 1, 1);
        if (self->first == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
        
        self->previous = gdk_pixbuf_new(GDK_COLORSPACE_RGB,
                                         FALSE, 8, 1, 1);
        if (self->previous == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }

        self->current = gdk_pixbuf_new(GDK_COLORSPACE_RGB,
                                        FALSE, 8, 1, 1);
        if (self->current == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
        self->timer = g_timer_new();
        g_timer_stop(self->timer);
        if (self->timer == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }

    }

    return (PyObject *)self;
}

static int
Videoprocessor_init(Videoprocessor *self, PyObject *args, PyObject *kwds)      
{
    
    
    return 0;
}

static PyMemberDef Videoprocessor_members[] = {
    {"timer", T_OBJECT_EX, offsetof(Videoprocessor, timer), 0,
     "timer"},
    {"threshold", T_OBJECT_EX, offsetof(Videoprocessor, threshold), 0,
     "threshold for moviment"},
    {NULL}  /* Sentinel */
};

static GdkPixbuf *
Videoprocessor_getfirst(Videoprocessor *self, void *closure)
{
    g_object_ref(self->first);
    return self->first;
}

static int
Videoprocessor_setfirst(Videoprocessor *self, GdkPixbuf *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the 'first' attribute");
    return -1;
  }
  
  if (!GDK_IS_PIXBUF(value)) {
    PyErr_SetString(PyExc_TypeError, 
                    "The 'first' attribute value must be a pixbuf");
    return -1;
  }
      
  g_object_unref(self->first);
  g_object_ref(value);
  self->first = value;

  return 0;
}

static GdkPixbuf *
Videoprocessor_getprevious(Videoprocessor *self, void *closure)
{
    g_object_ref(self->previous);
    return self->previous;
}

static int
Videoprocessor_setprevious(Videoprocessor *self, GdkPixbuf *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the 'previous' attribute");
    return -1;
  }
  
  if (!GDK_IS_PIXBUF(value)) {
    PyErr_SetString(PyExc_TypeError, 
                    "The 'previous' attribute value must be a pixbuf");
    return -1;
  }
      
  g_object_unref(self->previous);
  g_object_ref(value);
  self->previous = value;

  return 0;
}

static GdkPixbuf *
Videoprocessor_getcurrent(Videoprocessor *self, void *closure)
{
    g_object_ref(self->current);
    return self->current;
}

static int
Videoprocessor_setcurrent(Videoprocessor *self, GdkPixbuf *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the 'current' attribute");
    return -1;
  }
  
  if (! GDK_IS_PIXBUF(value)) {
    PyErr_SetString(PyExc_TypeError, 
                    "The 'current' attribute value must be a pixbuf");
    return -1;
  }
      
  g_object_unref(self->current);
  g_object_ref(value);
  self->current = value;

  return 0;
}

/*
static PyGetSetDef Videoprocessor_getseters[] = {
    {"first", 
     (getter)Videoprocessor_getfirst, (setter)Videoprocessor_setfirst,
     "first pixbuf",
     NULL},
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
*/

static PyObject *
Videoprocessor_start_timer(Videoprocessor* self)
{
    g_timer_start(self->timer);
    return Py_BuildValue("i", 0);
}

static PyObject *
Videoprocessor_stop_timer(Videoprocessor* self)
{
    g_timer_stop(self->timer);
    return Py_BuildValue("i", 0);
}

static PyObject *
Videoprocessor_elapsed_time(Videoprocessor* self)
{
    gdouble result = g_timer_elapsed(self->timer, NULL);
    return Py_BuildValue("d", result) ;
}

/*
static PyObject *
Videoprocessor_name(Noddy* self)
{
    static PyObject *format = NULL;
    PyObject *args, *result;

    if (format == NULL) {
        format = PyString_FromString("%s %s");
        if (format == NULL)
            return NULL;
    }

    if (self->first == NULL) {
        PyErr_SetString(PyExc_AttributeError, "first");
        return NULL;
    }

    if (self->last == NULL) {
        PyErr_SetString(PyExc_AttributeError, "last");
        return NULL;
    }

    args = Py_BuildValue("OO", self->first, self->last);
    if (args == NULL)
        return NULL;

    result = PyString_Format(format, args);
    Py_DECREF(args);
    
    return result;
} */

static PyMethodDef Videoprocessor_methods[] = {
    {"startTimer", (PyCFunction)Videoprocessor_start_timer, METH_NOARGS,
     "Start the experiment timer"
    },
    {"stopTimer", (PyCFunction)Videoprocessor_stop_timer, METH_NOARGS,
     "Stop the experiment timer"
    },
    {"elapsedTime", (PyCFunction)Videoprocessor_elapsed_time, METH_NOARGS,
     "Return time elapsed"
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject VideoprocessorType = {
    PyObject_HEAD_INIT(NULL)
    0,                                           /*ob_size*/
    "videoprocessor.Videoprocessor",             /*tp_name*/
    sizeof(Videoprocessor),                      /*tp_basicsize*/
    0,                                           /*tp_itemsize*/
    (destructor)Videoprocessor_dealloc,          /*tp_dealloc*/
    0,                                           /*tp_print*/
    0,                                           /*tp_getattr*/
    0,                                           /*tp_setattr*/
    0,                                           /*tp_compare*/
    0,                                           /*tp_repr*/
    0,                                           /*tp_as_number*/
    0,                                           /*tp_as_sequence*/
    0,                                           /*tp_as_mapping*/
    0,                                           /*tp_hash */
    0,                                           /*tp_call*/
    0,                                           /*tp_str*/
    0,                                           /*tp_getattro*/
    0,                                           /*tp_setattro*/
    0,                                           /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,    /*tp_flags*/
    "videoprocessor object",                     /* tp_doc */
    0,                                           /* tp_traverse */
    0,                                           /* tp_clear */
    0,                                           /* tp_richcompare */
    0,                                           /* tp_weaklistoffset */
    0,                                           /* tp_iter */
    0,                                           /* tp_iternext */
    Videoprocessor_methods,                      /* tp_methods */
    Videoprocessor_members,                      /* tp_members */
    0, //Videoprocessor_getseters,               /* tp_getset */
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

    if (PyType_Ready(&VideoprocessorType) < 0)
        return;

    m = Py_InitModule3("videoprocessor", module_methods,
                       "Module used in video processing.");

    if (m == NULL)
        return;

    Py_INCREF(&VideoprocessorType);
    PyModule_AddObject(m, "Videoprocessor", 
                       (PyObject *)&VideoprocessorType);
}
























/*
GTimer* timer;
gdouble elapsed_time();
void start_timer();
void stop_timer();
void init_timer();

guint threshold;

guint32 get_threshold(void);

void set_threshold(guint32 t);

guint menorx, menory, maiorx, maiory, initial_control;
guint add, cont, i2;
guint m_x, m_y, mn_x, mn_y;
guint pxi, pyi, pxf, pyf;
gdouble tamanho;
gdouble escala;

void set_pxi(gint s);
gint get_pxi();

void set_pyi(gint s);
gint get_pyi();

void set_pxf(gint s);
gint get_pxf();

void set_pyf(gint s);
gint get_pyf();

void set_tamanho(gdouble s);
gdouble get_tamanho();

void set_escala(gdouble s);
gdouble get_escala();

void set_i2(gint s);
gint get_i2();

void set_initial_control(guint s);

guint get_initial_control(void);

void set_menorx(guint s);

guint get_menorx();

void set_maiorx(guint s);

guint get_maiorx();

void set_menory(guint s);

guint get_menory();

void set_maiory(guint s);

guint get_maiory();

void set_m_x(guint s);

guint get_m_x();

void set_m_y(guint s);

guint get_m_y();

void set_mn_x(guint s);

guint get_mn_x();

void set_mn_y(guint s);

guint get_mn_y();

GdkPixbuf* first;
GdkPixbuf* get_first(void);
void set_first(GdkPixbuf* set);

GdkPixbuf* previous;
GdkPixbuf* get_previous(void);
void set_previous(GdkPixbuf* set);

GdkPixbuf* current;
GdkPixbuf* get_current(void);
void set_current(GdkPixbuf* set);

GdkPixbuf* refimage;
GdkPixbuf* get_refimage(void);
void set_refimage(GdkPixbuf* set);

GdkPixbuf* track;
GdkPixbuf* get_track(void);
void set_track(GdkPixbuf* set);

gint process_video(UnicapgtkVideoDisplay* ugtk);

void init_pointers(void);

guint32 get_threshold(void)
{
    return threshold;
}

void set_threshold(guint32 s)
{
    threshold = s;
}

void set_i2(gint s)
{
    i2 = s;
}

gint get_i2()
{
    return i2;
}

void init_pointers(void)
{
    first = gdk_pixbuf_new (GDK_COLORSPACE_RGB,
                            FALSE, 8, 1, 1);
    current = gdk_pixbuf_new (GDK_COLORSPACE_RGB,
                            FALSE, 8, 1, 1);
    previous = gdk_pixbuf_new (GDK_COLORSPACE_RGB,
                            FALSE, 8, 1, 1);
    refimage = gdk_pixbuf_new (GDK_COLORSPACE_RGB,
                            FALSE, 8, 1, 1);
}


GdkPixbuf* get_first()
{
    return first;
}

void set_first(GdkPixbuf* set)
{
    g_object_unref(first);
    first = set;
    g_object_ref(first);
}

GdkPixbuf* get_current()
{
    return current;
}

void set_current(GdkPixbuf* set)
{
    g_object_unref(current);
    current = set;
    g_object_ref(current);
}

GdkPixbuf* get_previous()
{
    return previous;
}

void set_previous(GdkPixbuf* set)
{
    g_object_unref(previous);
    previous = set;
    g_object_ref(previous);
}

GdkPixbuf* get_refimage()
{
    return refimage;
}

void set_refimage(GdkPixbuf* set)
{
    g_object_unref(refimage);
    refimage = set;
    g_object_ref(refimage);
}

GdkPixbuf* get_track(void)
{
    return track;
}

void set_track(GdkPixbuf* set)
{
    g_object_unref(track);
    track = gdk_pixbuf_copy(set);
//    g_object_unref(track);
}


void set_initial_control(guint s)
{
    initial_control = s;
}

guint get_initial_control(void)
{
    return initial_control;
}

void set_menorx(guint s)
{
    menorx = s;
}

guint get_menorx()
{
    return menorx;
}

void set_maiorx(guint s)
{
    maiorx = s;
}

guint get_maiorx()
{
    return maiorx;
}

void set_menory(guint s)
{
    menory = s;
}

guint get_menory()
{
    return menory;
}

void set_maiory(guint s)
{
    maiory = s;
}

guint get_maiory()
{
    return maiory;
}

void set_m_x(guint s)
{
    m_x = s;
}

guint get_m_x()
{
    return m_x;
}

void set_m_y(guint s)
{
    m_y = s;
}

guint get_m_y()
{
    return m_y;
}

void set_mn_x(guint s)
{
    mn_x = s;
}

guint get_mn_x()
{
    return mn_x;
}

void set_mn_y(guint s)
{
    mn_y = s;
}

guint get_mn_y()
{
    return mn_y;
}

gdouble get_tamanho()
{
    return tamanho;
}

void set_tamanho(gdouble s)
{
    tamanho = s;
}

gdouble get_escala()
{
    return tamanho;
}

void set_escala(gdouble s)
{
    escala = s;
}

gdouble elapsed_time()
{
    return g_timer_elapsed(timer, NULL);
}

void start_timer()
{
    g_timer_start(timer);
}

void stop_timer()
{
    g_timer_stop(timer);
}

void init_timer()
{
    timer = g_timer_new();
    g_timer_stop(timer);
}

void set_pxi(gint s)
{
    pxi=s;
}

gint get_pxi()
{
    return pxi;
}

void set_pyi(gint s)
{
    pyi=s;
}

gint get_pyi()
{
    return pyi;
}

void set_pxf(gint s)
{
    pxf=s;
}

gint get_pxf()
{
    return pxf;
}

void set_pyf(gint s)
{
    pyf=s;
}

gint get_pyf()
{
    return pyf;
}

//
//    Responsavel por fazer todo o processamento das imagens capturadas
//    pela câmera.
//    Analisa em tempo real as imagens e detecta onde há movimento, e
//    verifica se é relevante ou não este movimento para o experimento,
//    ou se realmente o movimento é do objeto de interesse, e obtem as
//    coordenadas 'X' e 'Y' da posição atual do objeto de interesse.
//    Faz todos os cálculos de do movimento e verifica também em que
//    áea ativa o objeto analizado se encontra, e joga as imagens já
//    processadas em uma janela em tempo real.
//
//    Autor do algoritmo: Rogério Alan Cruz
//    Duvidas: rogerioalancruz@gmail.com
//
//    This algorithm was originally made for Windows
//    and is currently being adapted for Linux.

gint process_video(UnicapgtkVideoDisplay *ugtk)
{
    GdkPixbuf *pixbuf;

    pixbuf = unicapgtk_video_display_get_still_image( ugtk ); 
    
    guint32 data_threshold;
    data_threshold = get_threshold();

    gdouble start_time, end_time;    

    start_time = elapsed_time();

    switch (data_threshold)
    {
        case 0: 
                data_threshold = 0x06060600; 
                break;
        case 1: 
                data_threshold = 0x12121200; 
                break;
        case 2: 
                data_threshold = 0x18181800; 
                break;
        case 3: 
                data_threshold = 0x24242400; 
                break;
        case 4: 
                data_threshold = 0x30303000; 
                break;
        default:
                data_threshold = 0x06060600;
                break;
    }   
    
    if (get_initial_control() == 0)
    {
        set_current(pixbuf);
        set_previous(get_current());
        set_first(get_current());
        set_initial_control(1);
        set_maiorx(0);
        set_menorx(0);
        set_maiory(0);
        set_menory(0);
        set_i2(0);
        
    }
    else
    {
        set_first(get_previous());
        set_previous(get_current());
        set_current(pixbuf);
    }

    g_object_unref(pixbuf);

    gint xi, yi, xf, yf, 
         maiorx = get_maiorx(),
         menorx = get_menorx(), 
         maiory = get_maiory(), 
         menory = get_menory(),
         pxi = get_pxi(),
         pyi = get_pyf(),
         pxf = get_pxi(),
         pyf = get_pyf(),
         i2 = get_i2();
    
    if ( (menorx - 40) <= 0 )
        xi = 0;
    else
        xi = menorx - 40;

    if ( (menory - 40) <= 0 )
        yi = 0;
    else
        yi = menory - 40;

    if ( (maiorx + 40) > gdk_pixbuf_get_width(get_current()) )
        xf = gdk_pixbuf_get_height(current);
    else
        xf = maiorx + 40;

    if ( (maiory + 40) > gdk_pixbuf_get_height(get_current()) )
        yf = gdk_pixbuf_get_height(current);
    else
        yf = maiory + 40;

    guint m_x = get_m_x(), 
          m_y = get_m_y(),
          mn_x = get_mn_x(), 
          mn_y = get_mn_y(), 
          control2, control, mov;

    control = 0;
    control2 = 0;
    mov = 0;
    
    gdouble ajuste = 0.0;
    gdouble tamanho = get_tamanho();

    guint x;
    for (x=xi; (x<=xf) && (x<gdk_pixbuf_get_width(get_current())); x++)
    {
        guint y;
        for (y=yi; (y<=yf) && (y<gdk_pixbuf_get_height(get_current())); y++)
        {
            guint n_channels, rowstride;        
    
            guchar *pixels,
                   *current,
                   *previous;

            pixels = gdk_pixbuf_get_pixels(get_current());
            n_channels = gdk_pixbuf_get_n_channels(get_current());
            rowstride = gdk_pixbuf_get_rowstride(get_current());
    
            current = pixels + x * n_channels + y * rowstride;

            pixels = gdk_pixbuf_get_pixels(get_previous());
            n_channels = gdk_pixbuf_get_n_channels(get_previous());
            rowstride = gdk_pixbuf_get_rowstride(get_previous());
    
            previous = pixels + x * n_channels + y * rowstride;     

            guint32 pixel_previous;
            guint32 pixel_current;
    
            pixel_previous = (
                              (previous[0])<<24 | 
                              (previous[1])<<16 |
                              (previous[2])<<8 
                             );  

            pixel_current = (
                             (current[0])<<24 | 
                             (current[1])<<16 |
                             (current[2])<<8  
                            );    

            pixels = NULL; 
            current = NULL;
            previous = NULL;
        
            if ( ( pixel_current < ( pixel_previous - data_threshold ) ) || 
                 ( pixel_current > ( pixel_previous + data_threshold ) ) )
            {
                ajuste++;
                if (ajuste > tamanho )
                {
                    mov = 1;
                    if ( control2 == 0 )
                    {
                        maiorx = m_x;
                        menorx = mn_x;
                        maiory = m_y;
                        menory = mn_y;
                        control2 = 1;
                    }
                    if ( control == 0 )
                    {
                        menorx = x;
                        maiorx = x;
                        menory = y;
                        maiory = y;
                        control = 1;
                    }
                    else
                    {
                        if ( x > maiorx ) { maiorx=x; }
                        if ( x <=menorx ) { menorx=x; }
                        if ( y > maiory ) { maiory=y; }
                        if ( y <=menory ) { menory=y; }
                    }
                }
                else
                {
                    if( control == 0 )
                    {
                        mn_x = x;
                        m_x = x;
                        mn_y = y;
                        m_y = y; 
                        control = 1;
                    }
                    else
                    {
                        if( x > m_x ) { m_x = x; }
                        if( x <=mn_x) { mn_x = x; }
                        if( y > m_y ) { m_y = y; }
                        if( y <=mn_y) { mn_y = y; }
                    }
                }
            }
        }
    }

    if ( i2 == 0 )
    {
        if ( maiorx != xi )
        {
            if ( control == 1 )
            {
                pxi = (maiorx + menorx)/2; 
                pyi = (maiory + menory)/2; 
                i2 = 1;
            }
        }
    }
    else 
    {
        if ( maiorx != xi )
        {
            pxf = (maiorx + menorx)/2;   
            pyf = (maiory + menory)/2;
            
            g_printf("entrou\n");
            fflush(stdout);            

            GladeXML* xml;
            GtkWidget* track;
            GdkPixbuf* track_pixbuf;
            xml = get_xml();
            track = glade_xml_get_widget( xml, "trackPixbuf");

            gdk_draw_pixbuf (track->window,
                             track->style->fg_gc[GTK_STATE_NORMAL],
                             track_pixbuf,
                             0, 0, 0, 0, 
                             gdk_pixbuf_get_width(track_pixbuf),
                             gdk_pixbuf_get_height(track_pixbuf),
                             GDK_RGB_DITHER_NONE,
                             0, 0);

            gdk_draw_line (track->window,
                           track->style->fg_gc[GTK_STATE_NORMAL],
                           pxi, pyi,
                           pxf, pyf);            

             gdk_pixbuf_get_from_drawable (track_pixbuf,
                                           track->window,
                                           gdk_drawable_get_colormap(track->window),
                                           0, 0, 0, 0, 
                                           gdk_pixbuf_get_width(track_pixbuf),
                                           gdk_pixbuf_get_height(track_pixbuf) 
                                          );
            pxi = pxf; 
            pyi = pyf;
        }
    }

    guint m1 = 0,
          m2 = 30,
          mov2;
        
    if (mov == 0)
    {  
        if (ajuste == 0)
        {
            guint x;
            for (x = menorx + 1; (x <= maiorx) && (x<gdk_pixbuf_get_width(get_current())) && (x>0) ; x++)
            {
                guint y;
                for (y = menory + 1; (y <= maiory) && (y<gdk_pixbuf_get_height(get_current())) && (y>0) ; y++)
                {
                    guint n_channels, rowstride;
    
                    guchar *pixels, 
                           *current,
                           *first;

                    pixels = gdk_pixbuf_get_pixels (get_current());
                    n_channels = gdk_pixbuf_get_n_channels (get_current());
                    rowstride = gdk_pixbuf_get_rowstride (get_current());
    
                    current = pixels + x * n_channels + y * rowstride;

                    pixels = gdk_pixbuf_get_pixels (get_first());
                    n_channels = gdk_pixbuf_get_n_channels (get_first());
                    rowstride = gdk_pixbuf_get_rowstride (get_first());
    
                    first = pixels + x * n_channels + y * rowstride;     

                    guint32 pixel_first;
                    guint32 pixel_current;

                    pixel_first = (
                                    (first[0])<<24 | 
                                    (first[1])<<16 |
                                    (first[2])<<8 
                                   );            

                    pixel_current = (
                                     (current[0])<<24 | 
                                     (current[1])<<16 |
                                     (current[2])<<8  
                                    );  

                    pixels = NULL; 
                    current = NULL;
                    first = NULL;

                    g_free(pixels); 
                    g_free(current);
                    g_free(first);

                    if(( pixel_current < ( pixel_first - data_threshold ) ) )
                    {
                        m2++;
                    }
                    else
                    {
                        if ( ( pixel_current > ( pixel_first + data_threshold ) ) )
                        {
                            m1++;
                        }
                    }
                }
            }
        }
        if(m1 < m2)
        {
            gtk_statusbar_pop (GTK_STATUSBAR(statusbar),
                               gtk_statusbar_get_context_id 
                                    (GTK_STATUSBAR(statusbar), "movimento"));

            gtk_statusbar_push (GTK_STATUSBAR(statusbar), 
                                gtk_statusbar_get_context_id 
                                    (GTK_STATUSBAR(statusbar), "movimento"),
                                "Parado no espaço!");
       
            mov2 = 0;
        }
        else
        { 
            if( gtk_toggle_button_get_active ( GTK_TOGGLE_BUTTON(checkSearch) ) ) 
            { 
                gtk_statusbar_pop (GTK_STATUSBAR(statusbar),
                                   gtk_statusbar_get_context_id 
                                       (GTK_STATUSBAR(statusbar), "movimento"));
                gtk_statusbar_push (GTK_STATUSBAR(statusbar), 
                                    gtk_statusbar_get_context_id 
                                    (GTK_STATUSBAR(statusbar), "movimento"), 
                                    "Em movimento fora do espaço!");
                mov2 = 1;
            } 
        }
    }
    
    else
    {  
       gtk_statusbar_pop (GTK_STATUSBAR(statusbar),
                          gtk_statusbar_get_context_id 
                              (GTK_STATUSBAR(statusbar), "movimento"));
       gtk_statusbar_push (GTK_STATUSBAR(statusbar), 
                           gtk_statusbar_get_context_id
                               (GTK_STATUSBAR(statusbar), "movimento"), 
                           "Em movimento!");

        mov2 = 0;
    }

    if(mov2==0)
    {
        set_first(get_previous());
    }
    else
    {
        while( mov2 == 1 )
        {
            guint xii = xi;
            guint yii = yi;
            guint xff = xf;
            guint yff = yf;
            guint add = 40;
            while( ( mov2 == 1 ) && 
                   ( 
                     ( xii >= 0 )                                 ||
                     ( xff <= gdk_pixbuf_get_width(get_first()) ) ||
                     ( yii >= 0 )                                 ||
                     ( yff <= gdk_pixbuf_get_height(get_first())) 
                   )
                )
                {
                    guint control = 0;

                    pixbuf = unicapgtk_video_display_get_still_image( ugtk ); 
                    set_current(pixbuf);
                    
                    guint x;
                    if ( xii - add < 0 ) 
                        x = 0;
                    else 
                        x = xii-add;

                    guint y;
                    if ( yii - add < 0 )
                        y = 0;
                    else
                        y = yii-add;

                    for ( x; (x <= xff + add) && (gdk_pixbuf_get_width(get_first())) ; x++ )
                    {
                        for ( y; ( y <= yii ) ; y++ )
                        {

                            guint n_channels, rowstride;
    
                            guchar *pixels, 
                                   *current,
                                   *first;

                            pixels = gdk_pixbuf_get_pixels (get_current());
                            n_channels = gdk_pixbuf_get_n_channels (get_current());
                            rowstride = gdk_pixbuf_get_rowstride (get_current());
    
                            current = pixels + x * n_channels + y * rowstride;

                            pixels = gdk_pixbuf_get_pixels (get_first());
                            n_channels = gdk_pixbuf_get_n_channels (get_first());
                            rowstride = gdk_pixbuf_get_rowstride (get_first());
    
                            first = pixels + x * n_channels + y * rowstride;

                            guint32 pixel_first;
                            guint32 pixel_current;

                            pixel_first = (
                                            (first[0])<<24 | 
                                            (first[1])<<16 |
                                            (first[2])<<8 
                                           );            

                            pixel_current = (
                                             (current[0])<<24 | 
                                             (current[1])<<16 |
                                             (current[2])<<8  
                                            );  
                            pixels = NULL; 
                            current = NULL;
                            first = NULL;

                            g_free(pixels); 
                            g_free(current);
                            g_free(first);

                            if (  ( pixel_current < ( pixel_first - data_threshold )) 
                               || ( pixel_current > ( pixel_first + data_threshold )) )
                            {
                                mov2=0;
                                if(control==0)  
                                {
                                    menorx = x;
                                    maiorx = x;
                                    menory = y;
                                    maiory = y;
                                    control = 1;
                                }
                                else
                                {
                                    if(x >  maiorx) { maiorx = x; }
                                    if(x <= menorx) { menorx = x; }
                                    if(y >  maiory) { maiory = y; }
                                    if(y <= menory) { menory = y; }
                                }
                            }
                        }
                    }
                    if(mov2==1)
                    {
                        control=0;

                        guint x;
                        if ( xii - add < 0 ) 
                            x = 0;
                        else 
                            x = xii-add;

                        guint y;
 
                        for( x ; x <= xii ; x++)
                        {
                            for ( y = yii; y <= yff; y++)
                            {

                                guint n_channels, rowstride;
    
                                guchar *pixels, 
                                       *current,
                                       *first;

                                pixels = gdk_pixbuf_get_pixels (get_current());
                                n_channels = gdk_pixbuf_get_n_channels (get_current());
                                rowstride = gdk_pixbuf_get_rowstride (get_current());
    
                                current = pixels + x * n_channels + y * rowstride;

                                pixels = gdk_pixbuf_get_pixels (get_first());
                                n_channels = gdk_pixbuf_get_n_channels (get_first());
                                rowstride = gdk_pixbuf_get_rowstride (get_first());
    
                                first = pixels + x * n_channels + y * rowstride;

                                guint32 pixel_first;
                                guint32 pixel_current;

                                pixel_first = (
                                                (first[0])<<24 | 
                                                (first[1])<<16 |
                                                (first[2])<<8 
                                               );            

                                pixel_current = (
                                                 (current[0])<<24 | 
                                                 (current[1])<<16 |
                                                 (current[2])<<8  
                                                );  
                                pixels = NULL; 
                                current = NULL;
                                first = NULL;

                                g_free(pixels); 
                                g_free(current);
                                g_free(first);

                                if( ( pixel_current < ( pixel_first - data_threshold ))
                                   || (pixel_current > ( pixel_first + data_threshold )) )
                                {
                                    mov2=0;
                                    if(control==0) 
                                    {
                                        menorx=x;maiorx=x;
                                        menory=y;maiory=y;
                                        control=1;
                                    }
                                    else
                                    {
                                        if(x>maiorx) { maiorx=x; }
                                        if(x<=menorx) { menorx=x;  }
                                        if(y>maiory) { maiory=y;  }
                                        if(y<=menory) { menory=y; }
                                    }
                                }
                            }
                        }
                    }
                    
                    if(mov2==1)
                    {
                        control=0;
                        guint x;
                        guint y;

                        for ( x = xff;
                            ( x <= xff + add) && ( x < (gdk_pixbuf_get_width(get_first()))) ;
                              x++)
                        {
                            for ( y = yii; y <= yff; y++ )
                            {

                                guint n_channels, rowstride;
    
                                guchar *pixels, 
                                       *current,
                                       *first;

                                pixels = gdk_pixbuf_get_pixels (get_current());
                                n_channels = gdk_pixbuf_get_n_channels (get_current());
                                rowstride = gdk_pixbuf_get_rowstride (get_current());
    
                                current = pixels + x * n_channels + y * rowstride;

                                pixels = gdk_pixbuf_get_pixels (get_first());
                                n_channels = gdk_pixbuf_get_n_channels (get_first());
                                rowstride = gdk_pixbuf_get_rowstride (get_first());
    
                                first = pixels + x * n_channels + y * rowstride;

                                guint32 pixel_first;
                                guint32 pixel_current;

                                pixel_first = (
                                                (first[0])<<24 | 
                                                (first[1])<<16 |
                                                (first[2])<<8 
                                               );            

                                pixel_current = (
                                                 (current[0])<<24 | 
                                                 (current[1])<<16 |
                                                 (current[2])<<8  
                                                );
                                pixels = NULL; 
                                current = NULL;
                                first = NULL;

                                g_free(pixels); 
                                g_free(current);
                                g_free(first);

                                if( ( pixel_current < ( pixel_first - data_threshold ))
                                  || ( pixel_current > ( pixel_first + data_threshold )) )
                                {
                                    mov2=0;
                                    if(control==0) 
                                    {
                                        menorx=x;maiorx=x;
                                        menory=y;maiory=y;
                                        control=1;
                                    }
                                    else 
                                    {
                                        if(x>maiorx) { maiorx=x; }
                                        if(x<=menorx) { menorx=x;  }
                                        if(y>maiory) { maiory=y;  }
                                        if(y<=menory) { menory=y; }
                                    }
                                }
                            }
                        }
                    }
                    if(mov2==1)
                    {
                        control=0;
                        for (x=xii-add; x<=xff+add; x++)
                        {
                            for (y=yff; y<=yff+add; y++)
                            { 

                                guint n_channels, rowstride;
    
                                guchar *pixels, 
                                       *current,
                                       *first;

                                pixels = gdk_pixbuf_get_pixels (get_current());
                                n_channels = gdk_pixbuf_get_n_channels (get_current());
                                rowstride = gdk_pixbuf_get_rowstride (get_current());
    
                                current = pixels + x * n_channels + y * rowstride;

                                pixels = gdk_pixbuf_get_pixels (get_first());
                                n_channels = gdk_pixbuf_get_n_channels (get_first());
                                rowstride = gdk_pixbuf_get_rowstride (get_first());
    
                                first = pixels + x * n_channels + y * rowstride;

                                guint32 pixel_first;
                                guint32 pixel_current;

                                pixel_first = (
                                                (first[0])<<24 | 
                                                (first[1])<<16 |
                                                (first[2])<<8 
                                               );            

                                pixel_current = (
                                                 (current[0])<<24 | 
                                                 (current[1])<<16 |
                                                 (current[2])<<8  
                                                );
                                pixels = NULL; 
                                current = NULL;
                                first = NULL;

                                g_free(pixels); 
                                g_free(current);
                                g_free(first);

                                if( ( pixel_current < ( pixel_first - data_threshold ) )
                                  || ( pixel_current > ( pixel_first + data_threshold ) ) )
                                {
                                    mov2=0;
                                    if(control==0)  
                                    {
                                        menorx=x;maiorx=x;
                                        menory=y;maiory=y;
                                        control=1;
                                    }
                                    else 
                                    {
                                        if(x>maiorx) { maiorx=x; }
                                        if(x<=menorx) { menorx=x;  }
                                        if(y>maiory) { maiory=y;  }
                                        if(y<=menory) { menory=y; }
                                    }
                                }
                            }
                        }
                    }

                    if( xii >= 40) { xii = xii-40; }
                    if( yii >= 40) { yii = yii-40; }
                    if( xff <= (gdk_pixbuf_get_width(get_current())- 40)) { xff = xff+40; }
                    if( yff <= (gdk_pixbuf_get_height(get_current())-40)) { yff = yff+40; }
                }
            
            if((mov2==1) && (xii<=0) &&
               (yii<=0) && (xff>=gdk_pixbuf_get_width(get_first())) &&
               (yff>=gdk_pixbuf_get_height(get_first()))
              )
            {
//                xii=Form4->get_xinicio(1);
//                yii=Form4->get_yinicio(1);
//                xff=Form4->get_xfim(1);
//                yff=Form4->get_yfim(1);
            }

        }
    }

    gdk_draw_pixbuf(track_display->window, 
                    track_display->style->fg_gc[GTK_STATE_NORMAL],
                    pixbuf,
                    0, 0,
                    0, 0,
                    -1, -1,
                    GDK_RGB_DITHER_NONE, 0, 0);

    gdk_draw_rectangle (track_display->window,
                        track_display->style->fg_gc[GTK_STATE_NORMAL],
                        FALSE,
                        xi,yi,
                        xf-xi,yf-yi);

    gdk_draw_rectangle (track_display->window,
                        track_display->style->fg_gc[GTK_STATE_NORMAL],
                        FALSE,
                        menorx, menory,
                        maiorx-menorx, maiory-menory);

    end_time = elapsed_time();

    GtkTreeIter iter;
   
    gtk_list_store_append (get_list(), &iter);
    gtk_list_store_set (get_list(), &iter,
                        COLUMN_START, start_time,
                        COLUMN_END, end_time,
                        COLUMN_X, (maiorx+menorx)/2,
                        COLUMN_Y, (maiory+menory)/2,
                        COLUMN_AREAS, 0,
                        -1);
  
    set_maiorx(maiorx); 
    set_menorx(menorx); 
    set_maiory(maiory); 
    set_menory(menory);
    set_m_x(m_x);
    set_m_y(m_y);
    set_mn_x(mn_x);
    set_mn_y(mn_y);
    set_pxi(pxi);
    set_pxf(pxf);
    set_pyi(pyi);
    set_pyf(pyf);

    gtk_widget_show_all(GTK_WIDGET(track_display));

    while( gtk_events_pending() )
    {
        gtk_main_iteration();
    }

    track_display = NULL;
    g_free(track_display); 
    statusbar = NULL;
    g_free(statusbar); 
    ugtk = NULL;
    g_free(ugtk);
    checkSearch = NULL;
    g_free(checkSearch);

    return TRUE;
}
*/
