#!/usr/bin/env python

from commands import getoutput
from distutils.core import setup, Extension

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

videoprocessor = Extension("videoprocessor",
                            include_dirs = includes,
                            libraries = libs,   
                            library_dirs = lib_dirs,
                            sources = ['src/videoprocessormodule.c'])

setup(name='SACAM',
      version='1.0',
      description='Sistema de Analise Comportamental de Animais em Movimento'
                  '/ Animal Motion Behavior Analysis System ',
      author='Luiz Carlos Irber Junior',
      author_email='luiz.irber@gmail.com',
      url='http://repositorio.agrolivre.gov.br/projects/sacam/',
      ext_modules = [videoprocessor],
      packages = ['sacam'],
      package_dir = { 'sacam': 'src' },
      package_data = { 'sacam': ['pixmaps/*.png'] }
     )
     