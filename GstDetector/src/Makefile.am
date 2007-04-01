# plugindir is set in configure

##############################################################################
# change libgstplugin.la to something more suitable, e.g. libmysomething.la  #
##############################################################################
plugin_LTLIBRARIES = libgstsacam.la

##############################################################################
# for the next set of variables, rename the prefix if you renamed the .la,   #
#  e.g. libgstplugin_la_SOURCES => libmysomething_la_SOURCES                 #
#       libgstplugin_la_CFLAGS  => libmysomething_la_CFLAGS                  #
#       libgstplugin_la_LIBADD  => libmysomething_la_LIBADD                  #
#       libgstplugin_la_LDFLAGS => libmysomething_la_LDFLAGS                 #
##############################################################################

# sources used to compile this plug-in
libgstsacam_la_SOURCES = gstsacam.c gstsacamdetector.c

# flags used to compile this plugin
# add other _CFLAGS and _LIBS as needed
libgstsacam_la_CFLAGS = $(GST_CFLAGS) \
                        $(GST_BASE_CFLAGS) \
                        $(GST_PLUGINS_BASE_CFLAGS) \
                        -I$(top_srcdir)/gst/videofilter -g
libgstsacam_la_LIBADD = $(GST_PLUGINS_BASE_LIBS) -lgstvideo-@GST_MAJORMINOR@ \
                        $(GST_BASE_LIBS) \
                        $(GST_LIBS)
libgstsacam_la_LDFLAGS = $(GST_PLUGIN_LDFLAGS)

# headers we need but don't want installed
noinst_HEADERS = gstsacam.h
