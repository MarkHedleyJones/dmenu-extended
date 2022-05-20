#! /usr/bin/env python
# -*- coding: utf8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='dmenu_extended',
      version='0.2.0',
      author='Mark Hedley Jones',
      author_email='markhedleyjones@gmail.com',
      description='A wrapper for dmenu that implements plugins and fast file/folder searching',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/markhedleyjones/dmenu-extended',
      packages=setuptools.find_packages(),
      classifiers=[
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      entry_points={
            'console_scripts': [
                  'dmenu_extended_run=dmenu_extended.main:run',
                  'dmenu_extended_build_cache=dmenu_extended.main:build_cache',
            ]
      },
      data_files=[('share/dmenu-extended/', ['scripts/systemd-install.sh']),
                  ('share/dmenu-extended/systemd', ['systemd/update-dmenu-extended-db.timer'])]
)
