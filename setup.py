# Created on 15-May-2013
from distutils.core import setup

setup(
	name='WebSnip',
	version='1.0dev',
	author='Aditya Basu',
	author_email='mitthu@adityabasu.me',
	
	packages=['websnip',],
	license='Creative Commons Attribution-Noncommercial-Share Alike license',
	description = "WebSnip is a utility to save web pages in an efficient manner.",
	long_description=open('README.rst').read(),
	install_requires=[
		'beautifulsoup4==4.1.3',
		'html5lib==0.95',
		'distribute==0.6.34',
    ]
)
