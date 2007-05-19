/* GStreamer
 * Copyright (C) <1999> Erik Walthinsen <omega@cse.ogi.edu>
 *
 * SACAM:
 * Copyright (C) 2007 Luiz Irber
 *
 * This library is free software; you can redistribute it and/or
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

#include "drawmethods.h"
#include "sacam-point.h"

G_BEGIN_DECLS

#define GST_TYPE_SACAMDETECTOR \
  (sacam_detector_get_type())
#define GST_SACAMDETECTOR(obj) \
  (G_TYPE_CHECK_INSTANCE_CAST((obj),GST_TYPE_SACAMDETECTOR,SacamDetector))
#define GST_SACAMDETECTOR_CLASS(klass) \
  (G_TYPE_CHECK_CLASS_CAST((klass),GST_TYPE_SACAMDETECTOR,SacamDetectorClass))
#define GST_IS_SACAMDETECTOR(obj) \
  (G_TYPE_CHECK_INSTANCE_TYPE((obj),GST_TYPE_SACAMDETECTOR))
#define GST_IS_SACAMDETECTOR_CLASS(klass) \
  (G_TYPE_CHECK_CLASS_TYPE((klass),GST_TYPE_SACAMDETECTOR))

typedef struct _SacamDetector      SacamDetector;
typedef struct _SacamDetectorClass SacamDetectorClass;

typedef struct {
    gint x_begin;
    gint y_begin;
    gint x_end;
    gint y_end;
} Window;

typedef struct {
    gint x_pos;
    gint y_pos;
    gchar start[24];
    gchar end[24];
} Point;

struct _SacamDetector
{
    GstVideoFilter videofilter;

    gint width, height, video_width_margin;
    gint map_width, map_height;
    guint32 *map, *canvas;

    GstBuffer *previous, *current;
    SacamDrawMethod draw_method;

    gdouble bug_size;
    guint32 threshold;
    Window tracking_area;
    gboolean silent, first_run, active;
    GList *points;
    gint tolerance;

};

struct _SacamDetectorClass
{
    GstVideoFilterClass parent_class;
};

GType sacam_detector_get_type (void);

G_END_DECLS

GST_DEBUG_CATEGORY_STATIC (sacamdetector_debug);
#define GST_CAT_DEFAULT sacamdetector_debug

enum
{
    LAST_SIGNAL
};

enum
{
    ARG_0,
    ARG_ACTIVE,
    ARG_DRAW,
    ARG_POINT_LIST,
    ARG_SILENT,
    ARG_SIZE,
    ARG_THRESHOLD,
    ARG_TOLERANCE,
    ARG_TRACKING_AREA
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

#define SACAM_TYPE_DRAW_METHOD (sacam_detector_draw_method_get_type())

static GType
sacam_detector_draw_method_get_type(void)
{
    static GType detector_draw_method_type = 0;
    static const GEnumValue detector_draw_methods[] = {
      {SACAM_DRAW_METHOD_NONE, "Don't draw anything", "none"},
      {SACAM_DRAW_METHOD_MASK, "Draw motion mask", "mask"},
      {SACAM_DRAW_METHOD_TRACK, "Draw motion track", "track"},
      {SACAM_DRAW_METHOD_BOX, "Draw motion box", "box"},
      {SACAM_DRAW_METHOD_MASK | SACAM_DRAW_METHOD_TRACK,
                              "Draw mask+track","mask+track"},
      {SACAM_DRAW_METHOD_MASK | SACAM_DRAW_METHOD_BOX,
                              "Draw mask+box", "mask+box"},
      {SACAM_DRAW_METHOD_TRACK | SACAM_DRAW_METHOD_BOX,
                              "Draw track+box", "track+box"},
      {SACAM_DRAW_METHOD_MASK | SACAM_DRAW_METHOD_TRACK |
       SACAM_DRAW_METHOD_BOX, "Draw all", "all"},
      {0, NULL, NULL},
    };

    if (!detector_draw_method_type) {
      detector_draw_method_type = g_enum_register_static ("SacamDetectorDrawMethods",
          detector_draw_methods);
    }

    return detector_draw_method_type;
}


static void sacam_detector_set_property (GObject * object, guint prop_id,
    const GValue * value, GParamSpec * pspec);
static void sacam_detector_get_property (GObject * object, guint prop_id,
    GValue * value, GParamSpec * pspec);
static gboolean sacam_detector_set_caps (GstBaseTransform * btrans,
    GstCaps * incaps, GstCaps * outcaps);
static gboolean sacam_detector_get_unit_size (GstBaseTransform * btrans,
    GstCaps * caps, guint * size);
static GstFlowReturn sacam_detector_transform (GstBaseTransform * trans,
    GstBuffer * in, GstBuffer * out);

static void
sacam_detector_base_init (gpointer g_class)
{
  GstElementClass *element_class = GST_ELEMENT_CLASS (g_class);

  static const GstElementDetails sacam_detector_details = {
      "Sacam Motion Detector",
      "Filter/Video",
      "Apply motion detection on video",
      "Luiz Irber <luiz.irber@gmail.com>"
  };

  gst_element_class_set_details (element_class, &sacam_detector_details);

  gst_element_class_add_pad_template (element_class,
      gst_static_pad_template_get (&sink_factory));
  gst_element_class_add_pad_template (element_class,
      gst_static_pad_template_get (&src_factory));
}

static void
sacam_detector_class_init (gpointer klass, gpointer class_data)
{
  GObjectClass *gobject_class;
  GstElementClass *element_class;
  GstBaseTransformClass *trans_class;

  gobject_class = (GObjectClass *) klass;
  element_class = (GstElementClass *) klass;
  trans_class = (GstBaseTransformClass *) klass;

  parent_class = g_type_class_peek_parent (klass);

  gobject_class->set_property = sacam_detector_set_property;
  gobject_class->get_property = sacam_detector_get_property;

  g_object_class_install_property (gobject_class, ARG_ACTIVE,
      g_param_spec_boolean ("active", "Active",
          "If True, process the input. Else just pass it away.",
          FALSE, G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_DRAW,
      g_param_spec_enum ("draw", "Draw method",
          "Set the drawing options",
          SACAM_TYPE_DRAW_METHOD, SACAM_DRAW_METHOD_TRACK,
          G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_SILENT,
      g_param_spec_boolean ("silent", "Silent", "Produce verbose output",
          TRUE, G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_THRESHOLD,
      g_param_spec_uint ("threshold", "Threshold",
          "Set the threshold for motion detection",
          0, 0xff, 0x30, /* min, max, default */
          G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_TOLERANCE,
      g_param_spec_uint ("tolerance", "Tolerance",
          "Set the tolerance for motion detection",
          0, G_MAXUINT, 0, /* min, max, default */
          G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_SIZE,
      g_param_spec_uint ("size", "Size",
          "Set the size of the object to be tracked",
          0, G_MAXUINT, 10, /* min, max, default */
          G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_TRACKING_AREA,
      g_param_spec_value_array ("tracking-area", "Tracking Area",
          "Current tracking area, in pixels",
          g_param_spec_int ("coord", "Coordinate part",
              "Holds part of the coordinate",
              0, 0xffffff, 0, G_PARAM_READWRITE),
          G_PARAM_READWRITE));

  g_object_class_install_property (gobject_class, ARG_POINT_LIST,
      g_param_spec_value_array ("point-list", "Point List",
          "Point list, in time order",
          g_param_spec_object ("point", "Point",
              "A point in the track",
              SACAM_TYPE_POINT, G_PARAM_READABLE),
          G_PARAM_READABLE));

  trans_class->set_caps = GST_DEBUG_FUNCPTR (sacam_detector_set_caps);
  trans_class->get_unit_size = GST_DEBUG_FUNCPTR (sacam_detector_get_unit_size);
  trans_class->transform = GST_DEBUG_FUNCPTR (sacam_detector_transform);
}

static void
sacam_detector_init (SacamDetector * filter,
                     SacamDetectorClass * gclass)
{
  SacamDetector *sacamdetector = GST_SACAMDETECTOR (filter);
  sacamdetector->map = NULL;
  sacamdetector->silent = TRUE;

  sacamdetector->tracking_area.x_begin = 0;
  sacamdetector->tracking_area.y_begin = 0;
  sacamdetector->tracking_area.x_end = 640;
  sacamdetector->tracking_area.y_end = 480;

  sacamdetector->active = FALSE;
  sacamdetector->first_run = TRUE;
  sacamdetector->threshold = 0x303030;
  sacamdetector->tolerance = 0;
  sacamdetector->bug_size = 10;
  sacamdetector->points = NULL;
  sacamdetector->draw_method = SACAM_DRAW_METHOD_TRACK;

  sacamdetector->current = gst_buffer_new();
  sacamdetector->previous = gst_buffer_new();

  /* TODO: initialize all the attributes */
}

static void
sacam_detector_set_property (GObject * object, guint prop_id,
                            const GValue * value, GParamSpec * pspec)
{
  SacamDetector *filter = GST_SACAMDETECTOR (object);

  switch (prop_id) {
    case ARG_ACTIVE:
      filter->active = g_value_get_boolean (value);
      break;
    case ARG_DRAW: {
      filter->draw_method = g_value_get_enum (value);
      break;
    }
    case ARG_SILENT:
      filter->silent = g_value_get_boolean (value);
      break;
    case ARG_THRESHOLD:
      filter->threshold = ( g_value_get_uint (value) << 16 |
                            g_value_get_uint (value) << 8  |
	                        g_value_get_uint (value)
                          );
      break;
    case ARG_TOLERANCE:
      filter->tolerance = g_value_get_uint (value);
      break;
    case ARG_SIZE:
      filter->bug_size = g_value_get_uint (value);
      break;
    case ARG_TRACKING_AREA: {
      GValueArray *va = g_value_get_boxed (value);
      int tmp;

      tmp = g_value_get_int(g_value_array_get_nth(va, 0));
      filter->tracking_area.x_begin = tmp;
      tmp = g_value_get_int(g_value_array_get_nth(va, 1));
      filter->tracking_area.y_begin = tmp;
      tmp = g_value_get_int(g_value_array_get_nth(va, 2));
      filter->tracking_area.x_end = tmp;
      tmp = g_value_get_int(g_value_array_get_nth(va, 3));
      filter->tracking_area.y_end = tmp;

      break;
    }
    case ARG_POINT_LIST:
      /* this should do nothing, because this property is read-only */
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}

static void
sacam_detector_get_property (GObject * object, guint prop_id,
                            GValue * value, GParamSpec * pspec)
{
  SacamDetector *filter = GST_SACAMDETECTOR (object);

  switch (prop_id) {
    case ARG_ACTIVE:
      g_value_set_boolean (value, filter->active);
      break;
    case ARG_DRAW:
      g_value_set_enum (value, filter->draw_method);
      break;
    case ARG_SILENT:
      g_value_set_boolean (value, filter->silent);
      break;
    case ARG_THRESHOLD:
      g_value_set_uint (value, filter->threshold & 0xff);
      break;
    case ARG_TOLERANCE:
      g_value_set_uint (value, filter->tolerance);
      break;
    case ARG_SIZE:
      g_value_set_uint (value, filter->bug_size);
      break;
    case ARG_TRACKING_AREA: {
      GValueArray *tmp_array;
      tmp_array = g_value_array_new(4);

      GValue tmp_value = { 0, };
      g_value_init(&tmp_value, G_TYPE_INT);

      g_value_set_int(&tmp_value, filter->tracking_area.x_begin);
      g_value_array_insert(tmp_array, 0, &tmp_value);

      g_value_set_int(&tmp_value, filter->tracking_area.y_begin);
      g_value_array_insert(tmp_array, 1, &tmp_value);

      g_value_set_int(&tmp_value, filter->tracking_area.x_end);
      g_value_array_insert(tmp_array, 2, &tmp_value);

      g_value_set_int(&tmp_value, filter->tracking_area.y_end);
      g_value_array_insert(tmp_array, 3, &tmp_value);

      g_value_set_boxed (value, tmp_array);
      break;
    }
    case ARG_POINT_LIST: {
      GValueArray *tmp_array;
      tmp_array = g_value_array_new(50);

      GValue tmp_value = {0,};
      g_value_init(&tmp_value, G_TYPE_OBJECT);

      GList* iter = filter->points;
      while (iter) {
          GObject *obj;
          obj = sacam_point_new_from_data(
                              ((Point*)(iter->data))->x_pos,
                              ((Point*)(iter->data))->y_pos,
                              ((Point*)(iter->data))->start,
                              ((Point*)(iter->data))->end
                              );

          g_value_set_object(&tmp_value, obj);
          g_value_array_prepend(tmp_array, &tmp_value);
          iter = iter->next;
      }

      g_value_set_boxed (value, tmp_array);
      break;
    }
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}

static gboolean
sacam_detector_set_caps (GstBaseTransform * btrans, GstCaps * incaps,
    GstCaps * outcaps)
{
  SacamDetector *sacamdetector = GST_SACAMDETECTOR (btrans);
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
sacam_detector_get_unit_size (GstBaseTransform * btrans, GstCaps * caps,
    guint * size)
{
  SacamDetector *filter;
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

static void _sacam_detector_set_current (SacamDetector *self,
                                         GstBuffer *buf)
{
    gst_buffer_unref(self->current);
    self->current = gst_buffer_copy(buf);
}

static void _sacam_detector_set_previous (SacamDetector *self,
                                             GstBuffer *buf)
{
    gst_buffer_unref(self->previous);
    self->previous = gst_buffer_copy(buf);
}

static void _draw_line (Point *current, Point *next, SacamDetector* filter)
{
    if ( next != NULL ) {
        __draw_line( filter->canvas, current->x_pos, current->y_pos,
                     next->x_pos, next->y_pos,
                     0xFF0000, filter->width, filter->height);
    }
    else
        return;
}

static void _create_point(Point* point, gint x_center, gint y_center,
                    struct timeval begin_time, struct timeval end_time)
{
      struct tm* ptm;
      long milliseconds;

      point->x_pos = x_center;
      point->y_pos = y_center;

      ptm = localtime (&begin_time.tv_sec);
      strftime (point->start, sizeof(point->start),"%Y-%m-%dT%H:%M:%S",ptm);
      milliseconds = begin_time.tv_usec / 1000;
      sprintf(point->start, "%s.%03ld", point->start, milliseconds);

      ptm = localtime (&end_time.tv_sec);
      strftime (point->end, sizeof(point->end), "%Y-%m-%dT%H:%M:%S", ptm);
      milliseconds = end_time.tv_usec / 1000;
      sprintf(point->end, "%s.%03ld", point->end, milliseconds);
}

static GstFlowReturn
sacam_detector_transform (GstBaseTransform * trans, GstBuffer * in,
                          GstBuffer * out)
{
  SacamDetector *filter;
  gint x, y;
  gint x_start, x_end, y_start, y_end;
  gint size, sum;
  gint x_center, y_center, width, height;
  gboolean window_is_defined;
  struct timeval begin_time, end_time;
  struct tm* ptm;
  long milliseconds;
  Point *point;

  tzset();

  GstFlowReturn ret = GST_FLOW_OK;

  filter = GST_SACAMDETECTOR (trans);

  gst_buffer_stamp (out, in);

  if (filter->active == TRUE) {
      if (filter->first_run == TRUE) {
          _sacam_detector_set_current(filter, in);
          _sacam_detector_set_previous(filter, in);
          filter->first_run = FALSE;

          return ret;
      }

      _sacam_detector_set_previous(filter, filter->current);
      _sacam_detector_set_current(filter, in);

      filter->canvas = (guint32 *) GST_BUFFER_DATA (out);

      size = filter->tracking_area.y_end - filter->tracking_area.y_begin;
      size = size / 2;
      if (size < filter->bug_size)
          size = filter->bug_size;
      sum =  filter->tracking_area.y_begin + filter->tracking_area.y_end;
      sum = sum / 2;
      y_start = sum - size;
      if (y_start < 0)
          y_start = 0;
      y_end = sum + size;
      if (y_end > filter->height)
          y_end = filter->height;

      size =  filter->tracking_area.x_end - filter->tracking_area.x_begin;
      size = size / 2;
      if (size < filter->bug_size)
          size = filter->bug_size;
      sum =  filter->tracking_area.x_end + filter->tracking_area.x_begin;
      sum = sum / 2;
      x_start = sum - size;
      if (x_start < 0)
          x_start = 0;
      x_end = sum + size;
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
                  if (filter->draw_method & SACAM_DRAW_METHOD_MASK)
                      filter->canvas[y*filter->width + x] = 0xff0000ff;
                  if (window_is_defined == TRUE) {
                      filter->tracking_area.y_end = y;
                      filter->tracking_area.x_end = x;
                  }
                  else {
                      filter->tracking_area.y_begin = y;
                      filter->tracking_area.x_begin = x;
                      filter->tracking_area.y_end = y;
                      filter->tracking_area.x_end = x;
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

      if (filter->draw_method & SACAM_DRAW_METHOD_BOX)
          _draw_rectangle (filter->canvas, filter->width, filter->height,
                        x_center, y_center, filter->bug_size, filter->bug_size);

      /* save the point on a list. data needed:
       * x_pos, y_pos, begin_time, end_time
       * x_pos and y_pos are the middle point of the filter->tracking_area
       *
       * To store the milliseconds, append it in the end of the timestamp.
       * Example: "%Y-%m-%dT%H:%M:%S.milliseconds"
       * */

      if (filter->points != NULL) {
          if ( ( abs(((Point*)(filter->points->data))->x_pos - x_center)
                 > filter->tolerance) ||
               ( abs(((Point*)(filter->points->data))->y_pos - y_center)
                 > filter->tolerance) ) {
             point = malloc( sizeof(Point) );
             _create_point (point, x_center, y_center, begin_time, end_time);
             filter->points = g_list_prepend(filter->points, point);
          }
          else {
              ptm = localtime (&end_time.tv_sec);
              strftime (((Point*)(filter->points->data))->end,
                        sizeof(((Point*)(filter->points->data))->end),
                        "%Y-%m-%dT%H:%M:%S", ptm);
              milliseconds = end_time.tv_usec / 1000;
              sprintf(((Point*)(filter->points->data))->end, "%s.%03ld",
                      ((Point*)(filter->points->data))->end, milliseconds);
          }
      }
      else {
          point = malloc( sizeof(Point) );
          _create_point (point, x_center, y_center, begin_time, end_time);
          filter->points = g_list_prepend(filter->points, point);
      }

      if (filter->silent == FALSE) {
          printf("%s delta: %ld.%ld\n", point->start,
              end_time.tv_sec - begin_time.tv_sec,
              end_time.tv_sec - begin_time.tv_usec);
              fflush(stdout);
      }

      if (filter->draw_method & SACAM_DRAW_METHOD_TRACK) {
          GList* iter = filter->points->next;
          while (iter) {
              GList *prev = iter->prev;
              _draw_line (iter->data, prev->data, filter);
              iter = iter->next;
          }
      }
  }
  return ret;
}


GType
sacam_detector_get_type (void)
{
  static GType sacam_detector_type = 0;

  if (!sacam_detector_type) {
    static const GTypeInfo sacam_detector_info = {
      sizeof (SacamDetectorClass),
      sacam_detector_base_init,
      NULL,
      (GClassInitFunc) sacam_detector_class_init,
      NULL,
      NULL,
      sizeof (SacamDetector),
      0,
      (GInstanceInitFunc) sacam_detector_init,
    };

    sacam_detector_type =
        g_type_register_static (GST_TYPE_VIDEO_FILTER, "SacamDetector",
        &sacam_detector_info, 0);
  }
  return sacam_detector_type;
}

