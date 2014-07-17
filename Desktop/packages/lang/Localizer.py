import locale

initDone = False
def initialize(langCode=None):
	loc = langCode
	if loc == None:
		loc = locale.getdefaultlocale()[0]
	global strings
	if loc.startswith("de"):
		import strings_de as strings
	else:
		import strings_en as strings


def String(key):
	return strings.strings[key]


print "INIT DE"
initialize()
print String("test")