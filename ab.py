test = u'didn\xb4t'
print test.find(u'\xb4')
print test.replace(u'\xb4', '\'')
print "came\u2026".find('\u2026')