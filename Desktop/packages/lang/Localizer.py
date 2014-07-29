import locale

initDone = False
def __initialize(langCode=None):
	if langCode == None:
		loc = locale.getdefaultlocale()
		if not loc == None:
			print "Default locale is ", loc
			langCode = loc[0]
		else:
			langCode = "EN"
		print "Language code: ", langCode
	global strings
	if langCode.lower().startswith("de"):
		import strings_de as strings
	else:
		# if locale not supported use english version
		import strings_en as strings
	global initDone
	initDone = True


def tr(key):
	if not initDone:
		print "Localizer not initialized..."
		__initialize()
	try:
		result = strings.strings[key]
	except:
		# in case invalid key is given
		result = key
	return result
