import os
from distutils.core import setup

# __version__ = None
# initFile = os.path.join(os.path.dirname(__file__), 'dmenu_extended', '__init__.py')
# for line in open(initFile).readlines():
#     if (line.startswith('version_info') or line.startswith('__version__')):
#         exec(line.strip())

# print("This is dmenu_extended v"+__version__)

setup(name='dmenu_extended',
      version='0.1.0',
      description='A wrapper for dmenu that implements plugins and fast file/folder searching',
      author='Mark H. Jones',
      author_email='markjones112358@gmail.com',
      url='https://github.com/markjones112358/dmenu-extended',
      py_modules=['dmenu_extended'],
      # packages=['dmenu_extended', 'dmenu_extended/config', 'dmenu_extended/plugins'],
      scripts=['dmenu_extended_run', 'dmenu_extended_cache_build'],
      data_files=[('share/dmenu-extended/', ['systemd-install.sh']),
                  ('share/dmenu-extended/systemd',
                      ['systemd/update-dmenu-extended-db.service',
                       'systemd/update-dmenu-extended-db.timer'])]
      )
