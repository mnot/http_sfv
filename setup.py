#!/usr/bin/env python

from setuptools import setup, find_packages
import shhh

setup(
  name = 'shhh',
  version = shhh.__version__,
  description = 'Structured HTTP Headers (handily)',
  long_description=open("README.md").read(),
  long_description_content_type="text/markdown",
  author = 'Mark Nottingham',
  author_email = 'mnot@mnot.net',
  license = "MIT",
  url = 'http://github.com/mnot/shhh/',
  download_url = 'http://github.com/mnot/thor/tarball/shhh-%s' % shhh.__version__,
  packages = find_packages(),
  provides = ['shhh'],
  python_requires=">=3.5",
  extras_require={
      'dev': [
          'mypy'
      ]
  },
  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Operating System :: POSIX',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ]
)
