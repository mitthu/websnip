# Started on 8-May-2013, 9:00 PM, by mitthu
# TODOs:
# Take care of url opening exceptions.
# Write test cases.
# References:
# http://stackoverflow.com/questions/10552188/python-split-url-to-find-image-name-and-extension

from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse, urljoin
from os.path import splitext, basename
import mimetypes
import codecs

from _log import Log
from _decorators import *

mimetypes.init()
links = {}
links['python'] = 'http://python.org/'
links['w3'] = 'http://www.w3schools.com/tags/tag_link.asp'
links['w3_1'] = 'http://www.w3schools.com/tags/att_script_src.asp'
links['django-debug'] = 'https://github.com/robhudson/django-debug-toolbar'
links['auto-complete'] = 'http://www2-pcmdi.llnl.gov/cdat/tips_and_tricks/python_tips/autocompletion.html'
links['doc-urllib'] = 'http://docs.python.org/2/howto/urllib2.html'
links['buggenie-issue'] = 'http://issues.thebuggenie.com/wiki/TheBugGenie%3AHowTo%3ANginxConfiguration'
links['python-signal'] = 'http://docs.python.org/2/library/signal.html'

# TODOs:
# Make all resources (html, css, scipts,...) unicode except images
class WebResource(object):
	def getMime(self):
		resource_mimetype = self.response.info()['Content-Type']
		# Taking care of content type with encoding,
		# ex. 'text/html; charset=UTF-8'
		resource_mimetype = resource_mimetype.split(';')[0]
		return resource_mimetype

	def getFilenameAndExtension(self):
		resource_extension = mimetypes.guess_extension(self.mime)
		if not resource_extension:
			guessed_mime = mimetypes.guess_type(self.url)[0]
			if guessed_mime:
				resource_extension = mimetypes.guess_extension(guessed_mime)
		# Parsing url and extracting filename and file_ext.
		# TODOs:
		# Look if the following os module functions work on windows also,
		# as windows path separator is '\'.
		url_parsed = urlparse(self.url)
		filename, file_ext = splitext(basename(url_parsed.path))
		if not resource_extension:
			resource_extension = file_ext
		if not resource_extension:
			self.log.info('Extension could not be guessed for url: %s' % self.url)
			resource_extension = '.none'
		return filename, resource_extension

	"""
	Parses the html structure using beautiful soup.
	"""
	def parseHtml(self):
		try:
			self.soup = BeautifulSoup(self.content, "html5lib")
		except:
			log.exception('Failed to parse: %s' % self.url)
			self.soup = None

	def renderHtml(self):
		return unicode(self.soup)

	def serialize(self):
		f = open(self.base_storage + self.filename, "w")
		f.write(self.content)
		f.close()

	@parsed
	def serializeUpdated(self):
		f = codecs.open(self.base_storage + self.filename, "w", "utf-8-sig")
		f.write(unicode(self.soup))
		f.close()

	def _is_absolute(self, url):
		if not url:
			return False
		return bool(urlparse(url).scheme)

	@parsed
	def updateNodeReferences(self, node, ref):
		for link in self.soup.find_all(node):
			link_attr = link.get(ref)
			if not self._is_absolute(link_attr):
				link.attrs[ref] = urljoin(self.url, link_attr);

	@parsed
	def cacheNodeReferences(self, node, ref):
		for link in self.soup.find_all(node):
			link_attr = link.get(ref)
			if link_attr:
				r = WebResource(link_attr, self.base_storage, self.user_agent)
				r.serialize()
				link.attrs[ref] = r.filename

	@parsed
	def updateReferences(self):
		self.updateNodeReferences('a', 'href')
		self.updateNodeReferences('a', 'src')
		self.updateNodeReferences('link', 'href')
		self.updateNodeReferences('img', 'src')
		self.updateNodeReferences('script', 'src')
		self.updated_references = True

	@parsed
	@updated_references
	def cacheReferencedResources(self):
		self.cacheNodeReferences('link', 'href')
		self.cacheNodeReferences('img', 'src')
		self.cacheNodeReferences('script', 'src')

	def cache(self):
		self.cacheReferencedResources()
		self.filename = 'index.html'
		self.serializeUpdated()

	"""WebResource"""
	def __init__(self, url, base_storage='cache/html/', user_agent='Mozilla/5.0', log='websnip.log'):
		super(WebResource, self).__init__()
		self.url = url
		self.base_storage = base_storage
		self.user_agent = user_agent
		self.log = Log(log)

		# TODOs:
		# Handle different types URL opening errors like if timeout, then retry.
		try:
			self.url_opener = urllib2.build_opener()
			self.url_opener.addheaders = [('User-agent', self.user_agent)]
			self.response = self.url_opener.open(self.url)
			self.content = self.response.read()
			self.mime = self.getMime()
		except:
			self.response = None
			self.content = None
			self.mime = None

		self.filebase, self.extension = self.getFilenameAndExtension()
		self.filename = self.filebase + self.extension

		self.soup = None
		self.updated_references = False
