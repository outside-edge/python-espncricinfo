#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="python-espncricinfo",
      version="0.2.3",
      description="ESPNCricInfo API client",
      license="MIT",
      install_requires=["requests"],
      author="Derek Willis",
      author_email="dwillis@gmail.com",
      url="http://github.com/dwillis/python-espncricinfo",
      packages = find_packages(),
      keywords= "espncricinfo cricket t20 odi",
      classifiers=['Development Status :: 4 - Beta'],
      zip_safe = True)
