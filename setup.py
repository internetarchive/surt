from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True

    def run_tests(self):
        import pytest
        import sys
        cmdline = ' -v --cov surt tests/'
        errcode = pytest.main(cmdline)
        sys.exit(errcode)


setup(name='surt',
      version='0.3.0',
      author='rajbot',
      author_email='raj@archive.org',
      classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3',
      ],
      description='Sort-friendly URI Reordering Transform (SURT) python package.',
      long_description=open('README.rst').read(),
      url='https://github.com/internetarchive/surt',
      zip_safe=True,
      install_requires=[
          'six',
          'tldextract>=2.0',
      ],
      provides=[ 'surt' ],
      packages=[ 'surt' ],
      scripts=[],
      # Tests
      tests_require=[ 'pytest', 'pytest-cov' ],
      test_suite='',
      cmdclass={'test': PyTest},
     )
