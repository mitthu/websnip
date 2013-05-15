from scrapper import *
url = 'http://stackoverflow.com/questions/9810104/sentry-raven-and-django-celery'
r = WebResource(url)
r.cache()

# python -m SimpleHTTPServer

def check_cache():
	# url = 'http://upload.wikimedia.org/wikipedia/commons/0/04/Np88_support.jpg'
	# url = 'http://stackoverflow.com/questions/9810104/sentry-raven-and-django-celery'

	# Failing Testes
	# 'http://web.appstorm.net/reviews/cloud-based-documents-contender-acrobat-com/'
	url = 'http://en.wikipedia.org/wiki/Byte_order_mark'
	WebResource(url).cache()

	url = 'http://stackoverflow.com/questions/9810104/sentry-raven-and-django-celery'
	r = WebResource(url)
	r.cache()

# TODOs:
# Take care of background images in stylesheets as well as inline styles (like  <a> tags in Wikiepedia Logo).
# Look if imports are possible in stylesheets/javascript and cache accordingly.
# Make resources handled as unicode.
# BUGs:
# Caching w3school pages gives error (@ top),
# 	<script src="http://www.googletagservices.com/tag/js/gpt.js"></script> 
# 'https' resources create trouble.
def cache_webpage(url):
	html = get_web_resource(url)
	try:
		soup = BeautifulSoup(html, "html5lib")
	except:
		logger.exception('Failed to parse: %s' % url)
		# return HttpResponse('Failed to parse url: %s' % url)
	update_node_reference(soup, 'a', 'href', url)
	update_node_reference(soup, 'a', 'src', url)
	serialize_and_update_node_reference(soup, 'link', 'href', url)
	serialize_and_update_node_reference(soup, 'img', 'src', url)
	serialize_and_update_node_reference(soup, 'script', 'src', url)
	serialize_content_to_file('index.html', unicode(soup))

def get_web_resource(url):
	response = urllib2.urlopen(url)
	html = response.read()
	return html

def is_absolute(url):
	if not url:
		return False
	return bool(urlparse(url).scheme)

def update_node_reference(markup, node, ref, url):
	for link in markup.find_all(node):
		link_attr = link.get(ref)
		if not is_absolute(link_attr):
			link.attrs[ref] = urljoin(url, link_attr);

def serialize_resource(url):
	html, filename = initalize_web_resource(url)
	serialize_content_to_file(filename, html.read())

def serialize_content_to_file(filename, content):
	f = open('cache/html/'+filename, 'w')
	f.write(content.encode('UTF-8'))
	f.close()

# TODOs:
# The function initalize_web_resource() unnecessarily fetches html. Improve it!
def serialize_and_update_node_reference(markup, node, ref, url):
	for link in markup.find_all(node):
		try:
			link_attr = link.attrs[ref]
			if not is_absolute(link_attr):
				link.attrs[ref] = urljoin(url, link.attrs[ref]);
			html, filename = initalize_web_resource(link.attrs[ref])
			serialize_resource(link.attrs[ref])
			link.attrs[ref] = filename
		except:
			pass
