from setuptools import setup
setup(name='surt',
      version='0.3b1',
      author='rajbot',
      author_email='raj@archive.org',
      classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3',
      ],
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
