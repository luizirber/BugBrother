#!/usr/bin/env python
#
# Copyright (C) 2006 by Embrapa Instrumentacao Agricola
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# This file contains code from Gazpacho
# Copyright (C) 2005 by Async Open Source

import os

from kiwi.environ import Library

dirname = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

lib = Library('sacam', root=dirname)
if lib.uninstalled:
    lib.add_global_resource('glade', 'glade')
    lib.add_global_resource('doc', 'doc')
    lib.add_global_resource('pixmap', 'pixmap')
lib.enable_translation()

