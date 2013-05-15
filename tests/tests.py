from websnip import *
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
