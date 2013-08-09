from setuptools import setup
setup(name='surt',
      version='0.2',
      author='rajbot',
      author_email='raj@archive.org',
      description='Sort-friendly URI Reordering Transform (SURT) python package.',
      long_description=open('README.md').read(),
      url='https://github.com/rajbot/surt',
      install_requires=[
          'tldextract',
      ],
      provides=[ 'surt' ],
      packages=[ 'surt' ],
      scripts=[],
     )
