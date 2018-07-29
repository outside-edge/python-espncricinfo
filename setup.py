from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="python-espncricinfo",
      version="0.3.2",
      description="ESPNCricInfo API client",
      license="MIT",
      install_requires=["requests", "bs4", "dateparser"],
      author="Derek Willis",
      author_email="dwillis@gmail.com",
      url="http://github.com/dwillis/python-espncricinfo",
      packages = find_packages(),
      keywords= "espncricinfo cricket t20 odi",
      classifiers=['Development Status :: 4 - Beta'],
      zip_safe = True)
