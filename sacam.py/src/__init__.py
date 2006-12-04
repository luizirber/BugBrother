import locale
import gettext
APP_NAME = "sacam"

#Translation stuff

#Get the local directory since we are not installing anything
self.local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
print self.local_path
# Init the list of languages to support
langs = []
#Check the default locale
lc, encoding = locale.getdefaultlocale()
if (lc):
    #If we have a default, it's the first in the list
    langs = [lc]
# Now lets get all of the supported languages on the system
language = os.environ.get('LANGUAGE', None)
if (language):
    """langage comes back something like en_CA:en_US:en_GB:en
    on linuxy systems, on Win32 it's nothing, so we need to
    split it up into a list"""
    langs += language.split(":")
"""Now add on to the back of the list the translations that we
know that we have, our defaults"""
langs += ["pt_BR"]

"""Now langs is a list of all of the languages that we are going
to try to use.  First we check the default, then what the system
told us, and finally the 'known' list"""

gettext.bindtextdomain(APP_NAME, self.local_path)
gettext.textdomain(APP_NAME)
# Get the language to use
self.lang = gettext.translation(APP_NAME, self.local_path,
                                languages=langs, fallback = True)
"""Install the language, map _() (which we marked our
strings to translate with) to self.lang.gettext() which will
translate them."""
_ = self.lang.gettext