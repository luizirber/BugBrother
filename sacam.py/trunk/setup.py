#!/usr/bin/env python

from commands import getoutput
from kiwi.dist import setup, listfiles, listpackages
from distutils.core import Extension

# flags used to compile the videoprocessor extension
cflags = getoutput('pkg-config gdk-2.0 glib-2.0 gtk+-2.0 '
                   'pygtk-2.0 pygobject-2.0 --cflags')
temp = cflags.replace('-I', '')
includes = temp.split()

libs_output = getoutput('pkg-config gdk-2.0 glib-2.0 gtk+-2.0 '
                        'pygtk-2.0 pygobject-2.0 --libs')
lib_dirs = []
libs = []
for item in libs_output.split():
    head, tail = item[:2], item[2:]
    if head == '-L':
        lib_dirs.append(tail)
    elif head == '-l':
        libs.append(tail)
    else:
        print "Warning: unused flags supplied by "\
              "`pkg-config glib-2.0 gdk-2.0 gtk+-2.0 "\
              "pygtk-2.0 pygobject-2.0 --libs`"

videoprocessor = Extension("sacam.cvideoprocessor",
                            include_dirs = includes,
                            libraries = libs,
                            library_dirs = lib_dirs,
                            sources = ['sacam/cvideoprocessor.c'])

data_files = [
     ('share/doc/sacam', ('AUTHORS', 'ChangeLog', 'CONTRIBUTORS',
                          'COPYING', 'README', 'NEWS')),
     ('share/doc/sacam', listfiles('doc', '*')),
     ('share/doc/sacam/examples', listfiles('examples', '*')),
     ('share/applications', listfiles('.', 'sacam.desktop')),
     ('$datadir/glade', listfiles('glade', '*.glade')),
     ('$datadir/glade', listfiles('glade', '*.png')),
     ('$datadir/xml', listfiles('xml', '*.rng'))
     ]

resources = dict(locale='$prefix/share/locale')
global_resources = dict(
     doc = '$prefix/share/doc/sacam',
     glade = '$datadir/glade',
     )

kwargs = {}
scripts = ['bin/sacam']

setup(name='sacam',
      version='1.0',
      description='Sistema de Analise Comportamental de Animais em Movimento'
                  '/ Animal Motion Behavior Analysis System ',
      author='Luiz Carlos Irber Junior',
      author_email='luiz.irber@gmail.com',
      url='http://repositorio.agrolivre.gov.br/projects/sacam/',
      license='GPL',
      ext_modules = [videoprocessor],
      packages = listpackages('sacam'),
      scripts = scripts,
      data_files = data_files,
      resources = resources,
      global_resources = global_resources,
      **kwargs
     )
