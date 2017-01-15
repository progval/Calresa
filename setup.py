#!/usr/bin/env python3

from setuptools import setup

with open('requirements.txt') as fd:
    install_requires = fd.read().split()

setup(name='calresa',
      version='0.1',
      description='Room booking viewer',
      author='Valentin Lorentz',
      author_email='progval+calresa@progval.net',
      url='https://github.com/ProgVal/Calresa',
      packages=['calresa'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Flask',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Natural Language :: French',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Office/Business :: Scheduling',
          ],
     )
