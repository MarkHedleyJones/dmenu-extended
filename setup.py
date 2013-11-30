import os
from distutils.core import setup

setup(name='dmenu_extended',
      version='1.0',
      description='A wrapper for dmenu that implements plugins and fast file/folder searching',
      author='Mark H. Jones',
      author_email='markjones112358@gmail.com',
      url='https://github.com/markjones112358/dmenu-extended',
      py_modules=['dmenu_extended'],
      data_files=[('/usr/bin', ['dmenu_extended_run'])]
      )