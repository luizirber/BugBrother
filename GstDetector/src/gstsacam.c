/* GStreamer
 * Copyright (C) <1999> Erik Walthinsen <omega@cse.ogi.edu>
 *
 * EffecTV:
 * Copyright (C) 2001 FUKUCHI Kentarou
 *
 * EffecTV is free software. This library is free software;
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

#include "gstsacam.h"

struct _elements_entry
{
  gchar *name;
    GType (*type) (void);
};

static struct _elements_entry _elements[] = {
  {"motiondetector", gst_sacamdetector_get_type},
  {NULL, 0},
};

static gboolean
plugin_init (GstPlugin * plugin)
{

  GST_DEBUG_CATEGORY_INIT (gst_sacam_debug, "Sacam",
      0, "Sacam Motion Detector and Tracking plugins");


  gint i = 0;

  while (_elements[i].name) {
    if (!gst_element_register (plugin, _elements[i].name,
            GST_RANK_NONE, (_elements[i].type) ()))
      return FALSE;
    i++;
  }

  return TRUE;
}

GST_PLUGIN_DEFINE (GST_VERSION_MAJOR,
    GST_VERSION_MINOR,
    "SACAM",
    "SACAM plugins for motion tracking and detection",
    plugin_init, VERSION, "GPL", GST_PACKAGE_NAME, GST_PACKAGE_ORIGIN);
