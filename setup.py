from setuptools import setup
setup(
  name = 'ofsc',         # How you named your package folder (MyLib)
  packages = ['ofsc'],   # Chose the same as "name"
  version = 'v1.8.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python Wrapper for Oracle Field Service API',   # Give a short description about your library
  author = 'Borja Toron',                   # Type in your name
  author_email = 'borja.toron@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/btoron/pyOFSC',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/btoron/pyOFSC/archive/v1.8.1.tar.gz',    # I explain this later on
  keywords = ['OFSC', 'Python', 'ORACLE FIELD SERVICE CLOUD', 'OFS', 'ORACLE FIELD SERVICE'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.8',
    ],
)
