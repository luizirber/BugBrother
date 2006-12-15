#/usr/bin/env python

import gettext
APP_NAME = "sacam"

_ = lambda msg: gettext.dgettext(APP_NAME, msg)
