#/usr/bin/env python

''' i18n module. 

    Provide the gettext _ function to make the translations.'''

import gettext
APP_NAME = "sacam"

_ = lambda msg: gettext.dgettext(APP_NAME, msg)
