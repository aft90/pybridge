import encodings

#
# GENERAL SETTINGS
#

# Copyright mark
coded=encodings.codecs.latin_1_decode('\xA9')
cmark=coded[0]

# Social
NAME="pybridge"
VERSION="0.0.0"
COPYRIGHT="Copyright " + cmark + " 2004 Michael Banks, Sourav K. Mandal"
COMMENTS="Online bridge made easy"
URL="http://pybridge.sourceforge.net/"
AUTHORS=('Michael Banks, Sourav K. Mandal')
AUTHORS_EMAIL=('umgangee@users.sourceforge.net, smandal@users.sourceforge.net')
DOCUMENTERS=()
TRANSLATOR_CREDITS="(No translations yet)"

#
# INTERNAL SETTINGS
#

# Unassigned according to Network Service Query
# Also, == factorial(7) :)
TCP_PORT=5040

