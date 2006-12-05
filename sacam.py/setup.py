#!/usr/bin/env python

from commands import getoutput
from kiwi.dist import setup, listfiles, listpackages
from distutils.core import Extension

from kiwi.dist import KiwiInstallLib, TemplateInstallLib

class InstallLib(TemplateInstallLib):
   name = 'sacam'
   global_resources = dict(glade='$datadir/glade',
                           pixmap='$datadir/pixmap')

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
                            sources = ['sacam/videoprocessormodule.c'])

setup(name='SACAM',
      version='1.0',
      description='Sistema de Analise Comportamental de Animais em Movimento'
                  '/ Animal Motion Behavior Analysis System ',
      author='Luiz Carlos Irber Junior',
      author_email='luiz.irber@gmail.com',
      url='http://repositorio.agrolivre.gov.br/projects/sacam/',
      ext_modules = [videoprocessor],
      packages = ['sacam'],
      package_dir = { 'sacam': 'sacam' },
      data_files=[('share/sacam/glade',
                  listfiles('glade', '*.glade')), 
                  ('share/sacam/pixmap',
                  listfiles('pixmap', '*.png'))],
      cmdclass=dict(install_lib=InstallLib))
    