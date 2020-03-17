#!/usr/bin/env python

from setuptools import setup, find_packages
import http_sfv

setup(
  name = 'http_sfv',
  version = http_sfv.__version__,
  description = 'Parse and serialise HTTP Structured Field Values',
  long_description=open("README.md").read(),
  long_description_content_type="text/markdown",
  author = 'Mark Nottingham',
  author_email = 'mnot@mnot.net',
  license = "MIT",
  url = 'http://github.com/mnot/http_sfv/',
  download_url = 'http://github.com/mnot/http_sfv/tarball/http_sfv-%s' % http_sfv.__version__,
  packages = find_packages(),
  provides = ['http_sfv'],
  python_requires=">=3.7",
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
    'Programming Language :: Python :: 3.7',
    'Operating System :: POSIX',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ]
)
