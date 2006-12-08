#/usr/bin/env python

import gettext
import locale
APP_NAME = "sacam"

_ = lambda msg: gettext.dgettext(APP_NAME, msg)
