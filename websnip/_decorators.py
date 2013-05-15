def updated_references(f):
	def inner(*args, **kwargs):
		instance = args[0]
		if not instance.updated_references:
			instance.updateReferences()
		return f(*args, **kwargs)
	return inner

def parsed(f):
	def inner(*args, **kwargs):
		instance = args[0]
		if not instance.soup:
			instance.parseHtml()
		if instance.soup:
			return f(*args, **kwargs)
	return inner

def deprecated(f):
	def inner(*args, **kwargs):
		print 'Using deprecated function: %s' % f.__name__
		return f(*args, **kwargs)
	return inner
