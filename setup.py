from distutils.core import setup
setup(name='surt',
      version='0.1',
      author='rajbot',
      author_email='raj@archive.org',
      description='Sort-friendly URI Reordering Transform (SURT) python package.',
      long_description=open('README.md').read(),
      url='https://github.com/rajbot/surt',
      requires=[
          'tldextract',
      ],
      provides=[ 'surt' ],
      packages=[ 'surt' ],
      scripts=[],
     )
