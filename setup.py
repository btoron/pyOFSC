from setuptools import setup
setup(
  name = 'ofsc',         
  packages = ['ofsc'],   
  version = 'v1.9',      
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python Wrapper for Oracle Field Service API',   
  author = 'Borja Toron',                
  author_email = 'borja.toron@gmail.com',   
  url = 'https://github.com/btoron/pyOFSC',   
  download_url = 'https://github.com/btoron/pyOFSC/archive/v1.9.tar.gz',    
  keywords = ['OFSC', 'Python', 'ORACLE FIELD SERVICE CLOUD', 'OFS', 'ORACLE FIELD SERVICE'],   # Keywords that define your package best
  install_requires=[            
          'requests',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.8',
    ],
)
