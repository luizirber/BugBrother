#ifndef DRAWMETHODS_H
#define DRAWMETHOD_H

#include <glib.h>

typedef enum {
    SACAM_DETECTOR_DRAW_METHOD_NONE  = 0,
    SACAM_DETECTOR_DRAW_METHOD_MASK  = 1 << 0,
    SACAM_DETECTOR_DRAW_METHOD_TRACK = 1 << 1,
    SACAM_DETECTOR_DRAW_METHOD_BOX   = 1 << 2,
} SacamDetectorDrawMethod;

void _draw_rectangle (guint32 *canvas, int canvas_width,
                      int canvas_height, int x_center, int y_center,
                      int rect_width, int rect_height);

void __draw_line (guint32 *data, int x1, int y1, int x2, int y2,
                  guint32 col, int screenx, int screeny);

#endif /*DRAWMETHODS_H*/
