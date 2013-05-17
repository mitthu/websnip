def valid_mime(f):
	def inner(*args, **kwargs):
		instance = args[0]
		# If MIME type is none/empty, then ...
		if not instance.mime:
			return None
		return f(*args, **kwargs)
	return inner

def updated_references(f):
	def inner(*args, **kwargs):
		instance = args[0]
		if not instance.updated_references:
			instance.update_node_references()
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
