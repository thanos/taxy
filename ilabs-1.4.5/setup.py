from distutils.core import setup, Extension

setup(name="ilabs", 
	version="1.4.5", 
	description="integrationsLabs' enterprise intergation framework", 
	author="Mark Tsang and Friends" ,
	author_email="ilabs@intergrationlabs.net",
	packages=['ilabs'],
      ext_modules=[Extension("cilabs", ["src/ilabs.c"])] ) 

	
