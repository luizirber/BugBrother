/* GStreamer
 * Copyright (C) <1999> Erik Walthinsen <omega@cse.ogi.edu>
 *
 * EffecTV:
 * Copyright (C) 2001 FUKUCHI Kentarou
 *
 * EffecTV is free software. * This library is free software;
 * you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 * 
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <string.h>
#include <time.h>
#include <sys/time.h>

#include <gst/video/gstvideofilter.h>
#include <gst/video/video.h>

G_BEGIN_DECLS

/* #defines don't like whitespacey bits */
#define GST_TYPE_SACAMDETECTOR \
  (gst_sacamdetector_get_type())
#define GST_SACAMDETECTOR(obj) \
  (G_TYPE_CHECK_INSTANCE_CAST((obj),GST_TYPE_SACAMDETECTOR,GstSacamDetector))
#define GST_SACAMDETECTOR_CLASS(klass) \
  (G_TYPE_CHECK_CLASS_CAST((klass),GST_TYPE_SACAMDETECTOR,GstSacamDetectorClass))
#define GST_IS_SACAMDETECTOR(obj) \
  (G_TYPE_CHECK_INSTANCE_TYPE((obj),GST_TYPE_SACAMDETECTOR))
#define GST_IS_SACAMDETECTOR_CLASS(klass) \
  (G_TYPE_CHECK_CLASS_TYPE((klass),GST_TYPE_SACAMDETECTOR))

typedef struct _GstSacamDetector      GstSacamDetector;
typedef struct _GstSacamDetectorClass GstSacamDetectorClass;

typedef struct {
    gint x_begin;
    gint y_begin;
    gint x_end;
    gint y_end;
} window;

struct _GstSacamDetector
{
    GstVideoFilter videofilter;

    gint width, height;
    gint map_width, map_height;
    guint32 *map;
    gint video_width_margin;

    GstBuffer *previous, *current;

    gdouble bug_size;

    guint32 threshold;

    window tracking_area;

    gboolean silent, first_run, active,
             draw_bounding_boxes, draw_track, draw_mask;
    
    GList *points;
};

struct _GstSacamDetectorClass 
{
    GstVideoFilterClass parent_class;
};

GType gst_sacamdetector_get_type (void);

G_END_DECLS

GST_DEBUG_CATEGORY_STATIC (gst_sacamdetector_debug);
#define GST_CAT_DEFAULT gst_sacamdetector_debug

enum
{
    LAST_SIGNAL
};

enum
{
    ARG_0,
    ARG_SILENT,
    ARG_THRESHOLD,
    ARG_SIZE,
    ARG_DRAW_BOXES,
    ARG_DRAW_TRACK,
    ARG_ACTIVE,
    ARG_DRAW_MASK
};

static GstStaticPadTemplate src_factory =
GST_STATIC_PAD_TEMPLATE ("src",
    GST_PAD_SRC,
    GST_PAD_ALWAYS,
    GST_STATIC_CAPS (GST_VIDEO_CAPS_BGRx)
    );

static GstStaticPadTemplate sink_factory =
GST_STATIC_PAD_TEMPLATE ("sink",
    GST_PAD_SINK,
    GST_PAD_ALWAYS,
    GST_STATIC_CAPS (GST_VIDEO_CAPS_BGRx)
    );

static GstVideoFilterClass *parent_class = NULL;

static void gst_sacamdetector_set_property (GObject * object, guint prop_id,
    const GValue * value, GParamSpec * pspec);
static void gst_sacamdetector_get_property (GObject * object, guint prop_id,
    GValue * value, GParamSpec * pspec);
static gboolean gst_sacamdetector_set_caps (GstBaseTransform * btrans, 
    GstCaps * incaps, GstCaps * outcaps);
static gboolean gst_sacamdetector_get_unit_size (GstBaseTransform * btrans, 
    GstCaps * caps, guint * size);
static GstFlowReturn gst_sacamdetector_transform (GstBaseTransform * trans,
    GstBuffer * in, GstBuffer * out);

static void
gst_sacamdetector_base_init (gpointer g_class)
{
  GstElementClass *element_class = GST_ELEMENT_CLASS (g_class);

  static const GstElementDetails sacamdetector_details = { 
      "Sacam Motion Detector",
      "Filter/Video",
      "Apply motion detection on video",
      "Luiz Irber <luiz.irber@gmail.com>"
  };

  gst_element_class_set_details (element_class, &sacamdetector_details);

  gst_element_class_add_pad_template (element_class,
      gst_static_pad_template_get (&sink_factory));
  gst_element_class_add_pad_template (element_class,
      gst_static_pad_template_get (&src_factory));
}

static void
gst_sacamdetector_class_init (gpointer klass, gpointer class_data)
{
  GObjectClass *gobject_class;
  GstElementClass *element_class;
  GstBaseTransformClass *trans_class;

  gobject_class = (GObjectClass *) klass;
  element_class = (GstElementClass *) klass;
  trans_class = (GstBaseTransformClass *) klass;

  parent_class = g_type_class_peek_parent (klass);

  gobject_class->set_property = gst_sacamdetector_set_property;
  gobject_class->get_property = gst_sacamdetector_get_property;
 
  g_object_class_install_property (gobject_class, ARG_ACTIVE,
      g_param_spec_boolean ("active", "Active",
          "If True, process the input. Else just pass it away.",
          FALSE, G_PARAM_READWRITE));
  
  g_object_class_install_property (gobject_class, ARG_DRAW_MASK,
      g_param_spec_boolean ("draw-mask", "Draw Motion Mask",
          "Draw the mask for the detected motion",
          FALSE, G_PARAM_READWRITE));
  
  g_object_class_install_property (gobject_class, ARG_DRAW_BOXES,
      g_param_spec_boolean ("draw-boxes", "Draw Bounding Boxes",
          "Draw the bounding boxes for the detected motion",
          FALSE, G_PARAM_READWRITE));
  
  g_object_class_install_property (gobject_class, ARG_DRAW_TRACK,
      g_param_spec_boolean ("draw-track", "Draw Track",
          "Draw the track captured until now",
          FALSE, G_PARAM_READWRITE));
  
  g_object_class_install_property (gobject_class, ARG_SILENT,
      g_param_spec_boolean ("silent", "Silent", "Produce verbose output",
          TRUE, G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_THRESHOLD,
      g_param_spec_uint ("threshold", "Threshold", 
          "Set the threshold for motion detection",
	  0, 0xff, 0x30, /* min, max, default */
          G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_SIZE,
      g_param_spec_uint ("size", "Size", 
          "Set the size of the object to be tracked",
	  0, 0xffffff, 30, /* min, max, default */
          G_PARAM_READWRITE));

  trans_class->set_caps = GST_DEBUG_FUNCPTR (gst_sacamdetector_set_caps);
  trans_class->get_unit_size = 
                       GST_DEBUG_FUNCPTR (gst_sacamdetector_get_unit_size);
  trans_class->transform = GST_DEBUG_FUNCPTR (gst_sacamdetector_transform);
}

static void
gst_sacamdetector_init (GstSacamDetector * filter, 
                        GstSacamDetectorClass * gclass)
{
  GstSacamDetector *sacamdetector = GST_SACAMDETECTOR (filter);

  sacamdetector->map = NULL;
  sacamdetector->silent = FALSE;

  sacamdetector->tracking_area.x_begin = 0;
  sacamdetector->tracking_area.y_begin = 0;
  sacamdetector->tracking_area.x_end = 640;
  sacamdetector->tracking_area.y_end = 480;
  
  sacamdetector->active = FALSE;
  sacamdetector->first_run = TRUE;
  sacamdetector->draw_mask = FALSE;
  sacamdetector->threshold = 0x303030;
  sacamdetector->bug_size = 30;
  sacamdetector->points = NULL;

  sacamdetector->current = gst_buffer_new();
  sacamdetector->previous = gst_buffer_new();

  /* TODO: initialize the attributes */
}

static void
gst_sacamdetector_set_property (GObject * object, guint prop_id,
    const GValue * value, GParamSpec * pspec)
{
  GstSacamDetector *filter = GST_SACAMDETECTOR (object);

  switch (prop_id) {
    case ARG_ACTIVE:
      filter->active = g_value_get_boolean (value);
      break;
    case ARG_DRAW_BOXES:
      filter->draw_bounding_boxes = g_value_get_boolean (value);
      break;
    case ARG_DRAW_MASK:
      filter->draw_mask = g_value_get_boolean (value);
      break;
    case ARG_DRAW_TRACK:
      filter->draw_track = g_value_get_boolean (value);
      break;
    case ARG_SILENT:
      filter->silent = g_value_get_boolean (value);
      break;
    case ARG_THRESHOLD:
      filter->threshold = ( g_value_get_uint (value) << 16 |
                            g_value_get_uint (value) << 8  |
			    g_value_get_uint (value)
                          );
      break;
    case ARG_SIZE:
      filter->bug_size = g_value_get_uint (value);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}

static void
gst_sacamdetector_get_property (GObject * object, guint prop_id,
    GValue * value, GParamSpec * pspec)
{
  GstSacamDetector *filter = GST_SACAMDETECTOR (object);

  switch (prop_id) {
    case ARG_ACTIVE:
      g_value_set_boolean (value, filter->active);
      break;
    case ARG_DRAW_BOXES:
      g_value_set_boolean (value, filter->draw_bounding_boxes);
      break;
    case ARG_DRAW_MASK:
      g_value_set_boolean (value, filter->draw_mask);
      break;
    case ARG_DRAW_TRACK:
      g_value_set_boolean (value, filter->draw_track);
      break;
    case ARG_SILENT:
      g_value_set_boolean (value, filter->silent);
      break;
    case ARG_THRESHOLD:         
      g_value_set_uint (value, filter->threshold & 0xff);
      break;
    case ARG_SIZE:
      g_value_set_uint (value, filter->bug_size);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}

static gboolean
gst_sacamdetector_set_caps (GstBaseTransform * btrans, GstCaps * incaps,
    GstCaps * outcaps)
{
  GstSacamDetector *sacamdetector = GST_SACAMDETECTOR (btrans);
  GstStructure *structure;
  gboolean ret = FALSE;

  structure = gst_caps_get_structure (incaps, 0);

  if (gst_structure_get_int (structure, "width", &sacamdetector->width) &&
      gst_structure_get_int (structure, "height", &sacamdetector->height)) {
    sacamdetector->map_width = sacamdetector->width / 4;
    sacamdetector->map_height = sacamdetector->height / 4;
    sacamdetector->video_width_margin = sacamdetector->width % 4;

    g_free (sacamdetector->map);
    sacamdetector->map =
        (guint32 *) g_malloc (sacamdetector->map_width *
	                      sacamdetector->map_height *
			      sizeof (guint32) * 2);
    memset (sacamdetector->map, 0,
            sacamdetector->map_width * sacamdetector->map_height 
            * sizeof (guint32) * 2);
    ret = TRUE;
  }

  return ret;
}

static gboolean
gst_sacamdetector_get_unit_size (GstBaseTransform * btrans, GstCaps * caps,
    guint * size)
{
  GstSacamDetector *filter;
  GstStructure *structure;
  gboolean ret = FALSE;
  gint width, height;

  filter = GST_SACAMDETECTOR (btrans);

  structure = gst_caps_get_structure (caps, 0);

  if (gst_structure_get_int (structure, "width", &width) &&
      gst_structure_get_int (structure, "height", &height)) {
    *size = width * height * 32 / 8;
    ret = TRUE;
    GST_DEBUG_OBJECT (filter, "our frame size is %d bytes (%dx%d)", *size,
        width, height);
  }

  return ret;
}

static void _gst_sacamdetector_set_current (GstSacamDetector *self, 
                                            GstBuffer *buf) 
{
    gst_buffer_unref(self->current);
    self->current = gst_buffer_copy(buf);
}

static void _gst_sacamdetector_set_previous (GstSacamDetector *self, 
                                             GstBuffer *buf)
{
    gst_buffer_unref(self->previous);
    self->previous = gst_buffer_copy(buf);
}

static void _draw_rectangle (guint32 *canvas, int canvas_width, 
                             int canvas_height, int x_center, int y_center,
                             int rect_width, int rect_height)
{
    int x, y;

    x = x_center - rect_width/2;
    if (x < 0)
        x = 0;

    y = y_center - rect_height/2;
    if (y < 0)
        y = 0;   

    for (x; (x < x_center + rect_width/2) && (x < canvas_width); x++)
        canvas[y*canvas_width + x] = 0x0;

    x = x_center - rect_width/2;
    if (x < 0)
        x = 0;

    for (y; (y < y_center + rect_height/2) && (y < canvas_height); y++) {
        canvas[y*canvas_width + x] = 0x0;
        if (y*canvas_width + x + rect_width < (y+1)*canvas_width)
            canvas[y*canvas_width + x + rect_width] = 0x0;
        else
            canvas[(y+1)*canvas_width - 1] = 0x0;
    }

    y--;
    for (x; (x < x_center + rect_width/2) && (x < canvas_width); x++)
        canvas[y*canvas_width + x] = 0x0;

}

static GstFlowReturn
gst_sacamdetector_transform (GstBaseTransform * trans, GstBuffer * in, 
                             GstBuffer * out)
{
  GstSacamDetector *filter;
  gint x, y;
  guint32 *dest;
  gint x_start, x_end, y_start, y_end;
  gint size;
  gint x_center, y_center, width, height;
  gboolean window_is_defined;
  struct timeval begin_time, end_time;

  tzset();
  
  GstFlowReturn ret = GST_FLOW_OK;

  filter = GST_SACAMDETECTOR (trans);

  gst_buffer_stamp (out, in);

  if (filter->active == TRUE) {
      if (filter->first_run == TRUE) {
          _gst_sacamdetector_set_current(filter, in);
          _gst_sacamdetector_set_previous(filter, in);
          filter->first_run = FALSE;
	  
	  return ret;
      }

      _gst_sacamdetector_set_previous(filter, filter->current);
      _gst_sacamdetector_set_current(filter, in);

      dest = (guint32 *) GST_BUFFER_DATA (out);

      size = (filter->tracking_area.y_end - filter->tracking_area.y_begin)/2;
      if (size < filter->bug_size)
          size = filter->bug_size;
      y_start = (filter->tracking_area.y_begin + filter->tracking_area.y_end)/2
              - size;
      if (y_start < 0)
          y_start = 0;
      y_end = (filter->tracking_area.y_begin + filter->tracking_area.y_end)/2
              + size;
      if (y_end > filter->height)
          y_end = filter->height;

      size = (filter->tracking_area.x_end - filter->tracking_area.x_begin)/2;
      if (size < filter->bug_size)
          size = filter->bug_size; 
      x_start = (filter->tracking_area.x_begin + filter->tracking_area.x_end)/2
                - size;
      if (x_start < 0)
          x_start = 0;
      x_end = (filter->tracking_area.x_begin + filter->tracking_area.x_end)/2
              + size;
      if (x_end > filter->width)
          x_end = filter->width;

      window_is_defined = FALSE;
      
      gettimeofday (&begin_time, &(struct timezone){timezone, daylight} );

      for (y = y_start; y < y_end; y++) {
          for (x = x_start; x < x_end; x++) {

              guint32 pixel_current, pixel_previous, min, max, *iter;

              iter = (guint32 *) GST_BUFFER_DATA (filter->current);
              pixel_current = iter[y*filter->width + x];

              iter = (guint32 *) GST_BUFFER_DATA (filter->previous);
              pixel_previous = iter[y*filter->width + x];

              if (pixel_previous > filter->threshold )
                  min = pixel_previous - filter->threshold;
              else
                  min = 0;

              if (pixel_previous > (0xffffff - filter->threshold) )
                  max = 0xffffffff;
              else
                  max = pixel_previous + filter->threshold;
                
              if ( (pixel_current < min ) || (pixel_current > max ) ) {
                  if (filter->draw_mask == TRUE)
                      dest[y*filter->width + x] = 0xff0000ff;
                  if (window_is_defined == TRUE) {
                      filter->tracking_area.y_end = y;
                      filter->tracking_area.x_end = x;
                  }
                  else {
                      filter->tracking_area.y_begin = y;
                      filter->tracking_area.x_begin = x;
                      filter->tracking_area.y_end= y;
                      filter->tracking_area.x_end= x;
                      window_is_defined = TRUE;
                  } 
              }
          }
      }

      gettimeofday (&end_time, NULL);
  
      width = filter->tracking_area.x_end - filter->tracking_area.x_begin;
      height = filter->tracking_area.y_end - filter->tracking_area.y_begin;
      x_center = filter->tracking_area.x_begin + width/2;
      y_center = filter->tracking_area.y_begin + height/2;
      /* TODO: verify if the bounding boxes must be drawn. */
      if (filter->draw_bounding_boxes == TRUE)
          _draw_rectangle (dest, filter->width, filter->height,
                           x_center, y_center, width, height);

      /* TODO: save the point on a list. data needed:
       * x_pos, y_pos, begin_time, end_time
       * x_pos and y_pos are the middle point of the filter->tracking_area 
       *
       * To store the milliseconds, append it in the end of the timestamp.
       * Example: "%Y-%m-%dT%H:%M:%S.milliseconds"
       * */

      struct tm* ptm;
      char time_string[40];
      long milliseconds;

      ptm = localtime (&begin_time.tv_sec);
      strftime (time_string, sizeof(time_string), "%Y-%m-%dT%H:%M:%S", ptm);
      milliseconds = begin_time.tv_usec / 1000;
      sprintf(time_string, "%s.%03ld\n", time_string, milliseconds);

      /* TODO: how to save the data? put on a struct, create a GObject? */

      /* TODO: which one is better? prepend and reverse, or just append? 
      filter->points = g_list_append(filter->points, data);
      
      filter->points = g_list_prepend(filter->points, data);
      filter->points = g_list_reverse(filter->points);
      */

      if (filter->silent == FALSE) {
	  printf("%s", time_string);
          printf("delta: %ld.%ld\n", 
	          end_time.tv_sec - begin_time.tv_sec, 
		  end_time.tv_sec - begin_time.tv_usec);
	  fflush(stdout);
      }

      /* TODO: verify if the track must be drawn. */
      if (filter->draw_track == TRUE) {
          printf("Track Drawn\n");
      }
  }
  return ret;
}

GType
gst_sacamdetector_get_type (void)
{
  static GType sacamdetector_type = 0;

  if (!sacamdetector_type) {
    static const GTypeInfo sacamdetector_info = {
      sizeof (GstSacamDetectorClass),
      gst_sacamdetector_base_init,
      NULL,
      (GClassInitFunc) gst_sacamdetector_class_init,
      NULL,
      NULL,
      sizeof (GstSacamDetector),
      0,
      (GInstanceInitFunc) gst_sacamdetector_init,
    };

    sacamdetector_type =
        g_type_register_static (GST_TYPE_VIDEO_FILTER, "SacamDetector",
        &sacamdetector_info, 0);
  }
  return sacamdetector_type;
}

