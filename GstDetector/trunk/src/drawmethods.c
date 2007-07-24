#include "drawmethods.h"

void _draw_rectangle (guint32 *canvas, int canvas_width,
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

    for (; (x < x_center + rect_width/2) && (x < canvas_width); x++) {
        canvas[y*canvas_width + x] = 0x0;
	if ((y + rect_height) * canvas_width + x < canvas_height * canvas_width)
            canvas[(y + rect_height) * canvas_width + x] = 0x0;
	else
	    canvas[(canvas_height - 1) * canvas_width + x] = 0x0;
    }

    x = x_center - rect_width/2;
    if (x < 0)
        x = 0;

    for (; (y < y_center + rect_height/2) && (y < canvas_height); y++) {
        canvas[y*canvas_width + x] = 0x0;
        if (y*canvas_width + x + rect_width < (y+1)*canvas_width)
            canvas[y*canvas_width + x + rect_width] = 0x0;
        else
            canvas[(y+1)*canvas_width - 1] = 0x0;
    }
}

void __draw_line (guint32 *data, int x1, int y1, int x2, int y2,
                  guint32 col, int screenx, int screeny)
{
  int     x, y, dx, dy, yy, xx;

  if ((y1 < 0) || (y2 < 0) || (x1 < 0) || (x2 < 0) || (y1 >= screeny) ||
      (y2 >= screeny) || (x1 >= screenx) || (x2 >= screenx))
      return;
  dx = x2 - x1;
  dy = y2 - y1;
  if (x1 > x2) {
    int tmp;

    tmp = x1;
    x1 = x2;
    x2 = tmp;
    tmp = y1;
    y1 = y2;
    y2 = tmp;
    dx = x2 - x1;
    dy = y2 - y1;
  }

  /* vertical line */
  if (dx == 0) {
    if (y1 < y2) {
      for (y = y1; y <= y2; y++) {
          data[(screenx * y) + x1] = col;
      }
    }
    else {
      for (y = y2; y <= y1; y++) {
         data[(screenx * y) + x1] = col;
      }
    }
    return;
  }
  /* horizontal line */
  if (dy == 0) {
    if (x1 < x2) {
      for (x = x1; x <= x2; x++) {
          data[(screenx * y1) + x] = col;
      }
      return;
    }
    else {
      for (x = x2; x <= x1; x++) {
          data[(screenx * y1) + x] = col;
      }
      return;
    }
  }
  /* 1    */
  /* \   */
  /* \  */
  /* 2 */
  if (y2 > y1) {
    /* steep */
    if (dy > dx) {
      dx = ((dx << 16) / dy);
      x = x1 << 16;
      for (y = y1; y <= y2; y++) {
          xx = x >> 16;
          data[(screenx * y) + xx] = col;
          if (xx < (screenx - 1)) {
              data[(screenx * y) + xx] = col;
          }
          x += dx;
      }
      return;
    }
    /* shallow */
    else {
      dy = ((dy << 16) / dx);
      y = y1 << 16;
      for (x = x1; x <= x2; x++) {
          yy = y >> 16;
          data[(screenx * yy) + x] = col;
          if (yy < (screeny - 1)) {
              data[(screenx * yy) + x] = col;
          }
          y += dy;
      }
    }
  }
  /* 2 */
  /* /  */
  /* /   */
  /* 1    */
  else {
    /* steep */
    if (-dy > dx) {
      dx = ((dx << 16) / -dy);
      x = (x1 + 1) << 16;
      for (y = y1; y >= y2; y--) {
          xx = x >> 16;
          data[(screenx * y) + xx] = col;
          if (xx < (screenx - 1)) {
              data[(screenx * y) + xx] = col;
          }
          x += dx;
      }
      return;
    }
    /* shallow */
    else {
      dy = ((dy << 16) / dx);
      y = y1 << 16;
      for (x = x1; x <= x2; x++) {
    	  yy = y >> 16;
          data[(screenx * yy) + x] = col;
    	  if (yy < (screeny - 1)) {
              data[(screenx * yy) + x] = col;
    	  }
    	  y += dy;
      }
      return;
    }
  }
}

