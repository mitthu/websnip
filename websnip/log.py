# Created by mitthu, on 2-March-2013

class Log(object):
	"""Log - Logging data to a file."""
	def log(self, content):
		self._start()
		self.f.write('Generic: '+content+'\n')
		self._end()

	def info(self, content):
		self._start()
		self.f.write('Info: '+content+'\n')
		self._end()

	def warn(self, content):
		self._start()
		self.f.write('Warn: '+content+'\n')
		self._end()

	def error(self, content):
		self._start()
		self.f.write('Error: '+content+'\n')
		self._end()

	def exception(self, content):
		self._start()
		self.f.write('Exception: '+content+'\n')
		self._end()

	def _start(self):
		self.f = open("datalog.log", "a")

	def _end(self):
		self.f.close()

	def __init__(self, filename):
		super(Log, self).__init__()
		self.filename = filename

# For global logging
logger = Log("datalog.log")
