from setuptools import setup
setup(name='surt',
      version='0.3',
      author='rajbot',
      author_email='raj@archive.org',
      classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
      ],
      description='Sort-friendly URI Reordering Transform (SURT) python package.',
      long_description=open('README.md').read(),
      url='https://github.com/rajbot/surt',
      install_requires=[
          'tldextract==1.6',
      ],
      provides=[ 'surt' ],
      packages=[ 'surt' ],
      scripts=[],
     )
