plugin_LTLIBRARIES = libgstsacam.la

# headers we need but don't want installed
noinst_HEADERS = gstsacam.h drawmethods.h sacam-point.h

#sources used to compile this plug-in
libgstsacam_la_SOURCES = gstsacam.c gstsacamdetector.c \
                         drawmethods.c sacam-point.c

#flags used to compile this plugin
# add other _CFLAGS and _LIBS as needed
libgstsacam_la_CFLAGS = $(GST_CFLAGS) \
                        $(GST_BASE_CFLAGS) \
                        $(GST_PLUGINS_BASE_CFLAGS) \
                        -I$(top_srcdir)/gst/videofilter -g
libgstsacam_la_LIBADD = $(GST_PLUGINS_BASE_LIBS) -lgstvideo-@GST_MAJORMINOR@ \
                        $(GST_BASE_LIBS) \
                        $(GST_LIBS)
libgstsacam_la_LDFLAGS = $(GST_PLUGIN_LDFLAGS)

