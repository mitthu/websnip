# Started on 8-May-2013, 9:00 PM, by mitthu
# TODOs:
# - Take care of url opening exceptions.
# - Write test cases.
# - Take care of background images in stylesheets as well as inline styles (like  <a> tags in Wikiepedia Logo).
# - Look if imports are possible in stylesheets/javascript and cache accordingly.
# - Make resources handled as unicode.
# - Write images as binary files.
# - Use python logging feature.
# - Take care or links starting with '#'

# BUGs:
# Caching w3school pages gives error (@ top),
# 	<script src="http://www.googletagservices.com/tag/js/gpt.js"></script> 
# 'https' resources create trouble.
# Control the amount of recursion in,
# - The number of levels the @import rules of css are met

# References:
# http://stackoverflow.com/questions/10552188/python-split-url-to-find-image-name-and-extension

from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse, urljoin
from os.path import splitext, basename
import mimetypes
import codecs
import re
import hashlib
import cssutils

from _log import Log
from _decorators import *

mimetypes.init()
links = {}
links['w3_1'] = 'http://www.w3schools.com/tags/att_script_src.asp'
links['auto-complete'] = 'http://www2-pcmdi.llnl.gov/cdat/tips_and_tricks/python_tips/autocompletion.html'
links['doc-urllib'] = 'http://docs.python.org/2/howto/urllib2.html'
links['buggenie-issue'] = 'http://issues.thebuggenie.com/wiki/TheBugGenie%3AHowTo%3ANginxConfiguration'
links['python-signal'] = 'http://docs.python.org/2/library/signal.html'

# Error prone
links['python'] = 'http://python.org/' # No styles come up, @import style directive
links['django-debug'] = 'https://github.com/robhudson/django-debug-toolbar' # Serialize problem
links['foobar'] = 'http://foobar.lu/wp/2012/05/13/a-comprehensive-step-through-python-packaging-a-k-a-setup-scripts/' # CSS background image
links['w3'] = 'http://www.w3schools.com/tags/tag_link.asp' # The <script> tag comes at the top

url = links['foobar']

# TODOs:
# Make all resources (html, css, scipts,...) unicode except images
class WebResource(object):
	def _is_absolute(self, url):
		if not url:
			return False
		return bool(urlparse(url).scheme)

	def _is_stylesheet(self):
		# If MIME type is none/empty, then ...
		if not self.mime:
			return False
		try:
			if self.mime.split('/')[1] == 'css':
				return True
		except:
			pass
		return False

	def _is_image(self):
		# If MIME type is none/empty, then ...
		if not self.mime:
			return False
		try:
			if self.mime.split('/')[0] == 'image':
				return True
		except:
			pass
		return False

	def getMime(self):
		resource_mimetype = self.response.info()['Content-Type']
		# Taking care of content type with encoding,
		# ex. 'text/html; charset=UTF-8'
		resource_mimetype = resource_mimetype.split(';')[0]
		return resource_mimetype

	def getFilenameAndExtension(self):
		resource_extension = None
		if self.mime:
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

	def contents_as_unicode(self):
		return unicode(self.content)

	def serialize(self):
		if self._is_stylesheet():
			sheet = cssutils.parseString(self.content, href=self.url)
			for rule in sheet.cssRules:
				if rule.type == rule.IMPORT_RULE:
					r = WebResource(rule.styleSheet.href, self.base_storage, self.user_agent, self.log)
					r.serialize()
					rule.href = r.url
			def replacer(url):
				if url.startswith('data'):
					return url
				r = WebResource(urljoin(self.url, url), self.base_storage, self.user_agent, self.log)
				r.serialize()
				return r.filename
			cssutils.replaceUrls(sheet, replacer, ignoreImportRules=True)
			self.content = sheet.cssText
		
		if self._is_image():
			f = open(self.base_storage + self.filename, "wb")
			f.write(self.content)
			f.close()
		else:
			f = open(self.base_storage + self.filename, "w")
			f.write(self.content)
			f.close()

	@parsed
	def serializeUpdated(self):
		f = codecs.open(self.base_storage + self.filename, "w", "utf-8-sig")
		f.write(unicode(self.soup))
		f.close()

	@parsed
	def update_node_references(self):
		# Getting the source (src) attribute corrected
		node_list = self.soup.find_all(src=re.compile(''))
		for node in node_list:
			link_attr = node.get('src')
			if not self._is_absolute(link_attr):
				node.attrs['src'] = urljoin(self.url, link_attr);

		# Getting the hyper-reference (href) attribute corrected
		node_list = self.soup.find_all(href=re.compile(''))
		for node in node_list:
			link_attr = node.get('href')
			if not self._is_absolute(link_attr):
				node.attrs['href'] = urljoin(self.url, link_attr);

		self.updated_references = True

	@parsed
	def cacheNodeReferences(self, node, ref):
		for link in self.soup.find_all(node):
			link_attr = link.get(ref)
			if link_attr:
				r = WebResource(link_attr, self.base_storage, self.user_agent, self.log)
				r.serialize()
				link.attrs[ref] = r.filename

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
	def __init__(self, url, base_storage='cache/', user_agent='Mozilla/5.0', log='websnip.log'):
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
			h = hashlib.md5()
			h.update(self.content)
			self.hash = h.hexdigest()
		except:
			self.response = None
			self.content = None
			self.mime = None
			self.hash = None

		self.filebase, self.extension = self.getFilenameAndExtension()
		if self.hash:
			self.filebase = self.filebase + '-' + self.hash[:8] # First 7 characters of md5 hash
		self.filename = self.filebase + self.extension

		self.soup = None
		self.updated_references = False

	@deprecated
	@parsed
	def updateNodeReferences(self, node, ref):
		for link in self.soup.find_all(node):
			link_attr = link.get(ref)
			if not self._is_absolute(link_attr):
				link.attrs[ref] = urljoin(self.url, link_attr);

	@deprecated
	@parsed
	def updateReferences(self):
		self.updateNodeReferences('a', 'href')
		self.updateNodeReferences('a', 'src')
		self.updateNodeReferences('link', 'href')
		self.updateNodeReferences('img', 'src')
		self.updateNodeReferences('script', 'src')
		self.updated_references = True
