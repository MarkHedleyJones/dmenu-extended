# -*- coding: utf8 -*-
#import commands
from __future__ import unicode_literals
import sys
import os
import subprocess
import signal
import json
import signal
import time

# Python 3 urllib import with Python 2 fallback
try:
    import urllib.request as urllib2
except:
    import urllib2

path_base = os.path.expanduser('~') + '/.config/dmenu-extended'
path_cache = path_base + '/cache'
path_prefs = path_base + '/config'
path_plugins = path_base + '/plugins'

file_prefs = path_prefs + '/dmenuExtended_preferences.json'
file_cacheScanned = path_cache + '/dmenuExtended_main.txt'
file_cachePlugins = path_cache + '/dmenuExtended_plugins.txt'
file_shCmd = '/tmp/dmenuEextended_shellCommand.sh'

default_prefs = {
    "valid_extensions": [
        "py",                   # Python script
        "svg",                  # Vector graphics
        "pdf",                  # Portable document format
        "txt",                  # Plain text
        "png",                  # Image file
        "jpg",                  # Image file
        "gif",                  # Image file
        "php",                  # PHP source-code
        "tex",                  # LaTeX document
        "odf",                  # Open document format
        "ods",                  # Open document spreadsheet
        "avi",                  # Video file
        "mpg",                  # Video file
        "mp3",                  # Music file
        "lyx",                  # Lyx document
        "bib",                  # LaTeX bibliograpy
        "iso",                  # CD image
        "ps",                   # Postscript document
        "zip",                  # Compressed archive
        "xcf",                  # Gimp image format
        "doc",                  # Microsoft document format
        "docx"                  # Microsoft document format
        "xls",                  # Microsoft spreadsheet format
        "xlsx",                 # Microsoft spreadsheet format
        "md",                   # Markup document
        "sublime-project"       # Project file for sublime
    ],
    "watch_folders": ["~/"],    # Base folders through which to search
    "follow_symlinks": False,   # Follow links to other locations 
    "ignore_folders": [],      # Folders to exclude from the search
    "include_items": [],        # Extra items to display - manually added
    "exclude_items": [],        # Items to hide - manually hidden
    "filter_binaries": True,    # Only include binaries that have a .desktop file
    "menu": 'dmenu',            # Executable for the menu
    "menu_arguments": [
        "-b",                   # Place at bottom of screen
        "-i",                   # Case insensitive searching
        "-nf",                  # Element foreground colour
        "#888888",
        "-nb",                  # Element background colour
        "#1D1F21",
        "-sf",                  # Selected element foreground colour
        "#ffffff",
        "-sb",                  # Selected element background colour
        "#1D1F21",
        "-fn",                  # Font and size
        "Terminus:12",
        "-l",                   # Number of lines to display
        "30" 
    ],
    "fileopener": "xdg-open",   # Program to handle opening files
    "filebrowser": "xdg-open",  # Program to handle opening paths
    "webbrowser": "xdg-open",   # Program to hangle opening urls
    "terminal": "xterm",        # Terminal
    "indicator_submenu": "-> ", # Symbol to indicate a submenu item
    "indicator_edit": "* "      # Symbol to indicate an item will launch an editor
}



def setup_user_files():
    """ Returns nothing

    Create a path for the users prefs files to be stored in their
    home folder. Create default config files and place them in the relevant
    directory.
    """

    print('Setting up dmenu-extended prefs files...')

    try:
        os.makedirs(path_plugins)
        print('Plugins directory created')
    except OSError:
        print('Plugins directory exists - skipped')

    try:
        os.makedirs(path_cache)
        print('Cache directory created')
    except OSError:
        print('Cache directory exists - skipped')

    try:
        os.makedirs(path_prefs)
        print('prefs directory created')
    except OSError:
        print('prefs directory exists - skipped')

    # If relevant binaries exist, swap them out for the safer defaults
    if os.path.exists('/usr/bin/gnome-open'):
        default_prefs['fileopener'] = 'gnome-open'
        default_prefs['webbrowser'] = 'gnome-open'
        default_prefs['filebrowser'] = 'gnome-open'
    if os.path.exists('/usr/bin/urxvt'):
        default_prefs['terminal'] = 'urxvt'

    # Dump the prefs file
    if os.path.exists(file_prefs) == False:
        with open(file_prefs,'w') as f:
            json.dump(default_prefs, f, sort_keys=True, indent=4)
        print('Preferences file created at: ' + file_prefs)
    else:
        print('Existing preferences file found, will not overwrite.')

    # Create package __init__ - for easy access to the plugins
    with open(path_plugins + '/__init__.py','w') as f:
        f.write('import os\n')
        f.write('import glob\n')
        f.write('__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]')


if (os.path.exists(path_plugins + '/__init__.py') and
    os.path.exists(file_cacheScanned) and
    os.path.exists(file_prefs)):
    sys.path.append(path_base)
else:
    setup_user_files()
    sys.path.append(path_base)

import plugins


def load_plugins():
    print('Loading plugins')
    plugins_loaded = []
    for plugin in plugins.__all__:
        if plugin != '__init__':
            try:
                __import__('plugins.' + plugin)
                exec('plugins_loaded.append({"filename": "' + plugin + '.py", "plugin": plugins.' + plugin + '.extension()})')
                print('Loaded plugin ' + plugin)
            except Exception as e:
                print('Error loading plugin ' + plugin)
                print(str(e))
                os.remove(path_plugins + '/' + plugin + '.py')
                print('!! Plugin was deleted to prevent interruption to dmenuExtended')
    return plugins_loaded


class dmenu(object):

    plugins_loaded = False
    prefs = False


    def get_plugins(self, force=False):
        """ Returns a list of loaded plugins

        This method will load plugins in the plugins directory if they
        havent already been loaded. Optionally, you may force the
        reloading of plugins by setting the parameter 'force' to true.
        """

        if self.plugins_loaded == False:
            self.plugins_loaded = load_plugins()
        elif force:
            print("Forced reloading of plugins")

            # For Python2/3 compatibility
            try:
                # Python2
                reload(plugins)
            except NameError:
                # Python3
                from imp import reload
                reload(plugins)

            self.plugins_loaded = load_plugins()

        return self.plugins_loaded


    def load_json(self, path):
        """ Loads and retuns the parsed contents of a specified json file

        This method will return 'False' if either the file does not exist
        or the specified file could not be parsed as valid json.
        """

        if os.path.exists(path):
            with open(path) as f:
                try:
                    return json.load(f)
                except:
                    print("Error parsing prefs from json file " + path)
                    return False
        else:
            print('Error opening json file ' + path)
            print('File does not exist')
            return False


    def save_json(self, path, items):
        """ Saves a dictionary to a specified path using the json format"""

        with open(path, 'w') as f:
            json.dump(items, f, sort_keys=True, indent=4)


    def load_preferences(self):
        if self.prefs == False:
            self.prefs = self.load_json(file_prefs)

            if self.prefs == False:
                self.open_file(file_prefs)
                sys.exit()
            else:
                for key, value in default_prefs.items():
                    if key not in self.prefs:
                        self.prefs[key] = value


    def save_preferences(self):
        save_json(file_prefs, self.prefs)


    def connect_to(self, url):
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        return response.read().decode('utf-8')


    def download_text(self, url):
        return self.connect_to(url)


    def download_json(self, url):
        return json.loads(self.connect_to(url))


    def message_open(self, message):
        self.load_preferences()
        self.message = subprocess.Popen([self.prefs['menu']] + self.prefs['menu_arguments'],
                                        stdin=subprocess.PIPE,
                                        preexec_fn=os.setsid)
        msg = str(message)
        msg = "Please wait: " + msg
        msg = msg.encode('utf-8')
        self.message.stdin.write(msg)
        self.message.stdin.close()


    def message_close(self):
        os.killpg(self.message.pid, signal.SIGTERM)


    def menu(self, items, prompt=False):
        self.load_preferences()
        if prompt == False:
            p = subprocess.Popen([self.prefs['menu']] + self.prefs['menu_arguments'],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen([self.prefs['menu']] + self.prefs['menu_arguments'] + ['-p', prompt],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)

        if type(items) == list:
            items = "\n".join(items)
        
        items = items.encode('utf-8')
        out = p.communicate(items)[0]

        if out.strip() == '':
            sys.exit()
        else:
            return out.decode().strip('\n')


    def select(self, items, prompt=None, numeric=False):
        result = self.menu(items, prompt)
        for index, item in enumerate(items):
            if result.find(item) != -1:
                if numeric:
                    return index
                else:
                    return item
        return -1


    def sort_shortest(self, items):
        items.sort(key=len)
        return items


    def open_url(self, url):
        self.load_preferences()
        print('Opening url: "' + url + '" with ' + self.prefs['webbrowser'])
        os.system(self.prefs['webbrowser'] + ' ' + url.replace(' ', '%20') + '&')


    def open_directory(self, path):
        self.load_preferences()
        print('Opening folder: "' + path + '" with ' + self.prefs['filebrowser'])
        os.system(self.prefs['filebrowser'] + ' "' + path + '"')


    def open_terminal(self, command, hold=False, direct=False):
        self.load_preferences()
        with open(file_shCmd, 'w') as f:
            f.write("#! /bin/bash\n")
            f.write(command + ";\n")
            
            if hold == True:
                f.write('echo "\nFinished\n\nPress any key to close terminal\n";')
                f.write('\nread var;')

        os.chmod(file_shCmd, 0o744)
        os.system(self.prefs['terminal'] + ' -e ' + file_shCmd) 


    def open_file(self, path):
        self.load_preferences()
        print('Opening file with command: ' + self.prefs['fileopener'] + " '" + path + "'")
        os.system(self.prefs['fileopener'] + " '" + path + "'")


    def execute(self, command, fork=None):
        if fork is not None:
            if fork == False:
                extra = ''
            else:
                extra = ' &'
        else:
            extra = ' &'
        os.system(command + extra)


    def cache_regenerate(self, debug=False, message=True):
        if message:
            self.message_open('building cache...')
        cache = self.cache_build(debug)
        if message:
            self.message_close()
        return cache


    def cache_save(self, items, location=False):
        if location == False:
            path = file_cacheScanned
        else:
            path = location

        try:
            with open(path, 'w') as f:
                if type(items) == list:
                    for item in items:
                        f.write(item+"\n")
                else:
                    f.write(items)
            return 1
        except UnicodeEncodeError:
            import string
            tmp = []
            foundError = False
            print('Non-printable characters detected in cache: ')
            for item in items:
                clean = True
                for char in item:
                    if char not in string.printable:
                        clean = False
                        foundError = True
                        print('Culprit: ' + item)
                if clean:
                    tmp.append(item)
            if foundError:
                print('')
                print('Caching performance will be affected while these items remain')
                print('Offending items have been excluded from cache')
                with open(path, 'wb') as f:
                    for item in tmp:
                        f.write(item+'\n')
                return 2
            else:
                print('Unknown error saving data cache')
                return 0


    def cache_open(self, location=False):
        if location == False:
            path = file_cacheScanned
        else:
            path = location

        try:
            print('Opening cache at ' + path)
            with open(path, 'r') as f:
                return f.read()
        except:
            return False


    def cache_load(self, exitOnFail=False):

        cache_plugins = self.cache_open(file_cachePlugins)
        cache_scanned = self.cache_open(file_cacheScanned)

        if cache_plugins == False or cache_scanned == False:
            if exitOnFail:
                print('The cache could not be opened, exiting')
                sys.exit()
            else:
                print('The cache was not loaded, attempting to regenerate...')
                if self.cache_regenerate() == False:
                    print('Cache regeneration failed')
                    self.menu(['Error caching data'])
                    sys.exit()
                else:
                    return self.cache_load(exitOnFail=True)

        return cache_plugins + cache_scanned


    def command_output(self, command, split=True):
        if type(command) != list:
            command = command.split(" ")
        tmp = subprocess.check_output(command)

        try:
            out = tmp.decode()
        except UnicodeDecodeError:
            out = tmp.decode('utf-8')
            
        if split:
            return out.split("\n")
        else:
            return out


    def scan_binaries(self, filter_binaries=False):
        out = []
        for binary in self.command_output("ls /usr/bin"):
            if filter_binaries:
                if os.path.exists('/usr/share/applications/' + binary + '.desktop'):
                    if binary[:3] != 'gpk':
                        out.append(binary)
            else:
                out.append(binary)

        return out


    def plugins_available(self, debug=False):
        self.load_preferences()
        print('Loading available plugins...')

        plugins = self.get_plugins(True)
        plugin_titles = []
        for plugin in plugins:
            if hasattr(plugin['plugin'], 'is_submenu') and plugin['plugin'].is_submenu:
                plugin_titles.append(self.prefs['indicator_submenu'] + plugin['plugin'].title)
            else:
                plugin_titles.append(plugin['plugin'].title)
        print('Done!')

        if debug:
            print('Plugins loaded:')
            print('First 5 items: ')
            print(plugin_titles[:5])
            print(str(len(plugin_titles)) + ' loaded in total')
            print('')

        out = self.sort_shortest(plugin_titles)
        self.cache_save(out, file_cachePlugins)

        return out


    def cache_build(self, debug=False):
        self.load_preferences()

        valid_extensions = []
        if 'valid_extensions' in self.prefs:
            for extension in self.prefs['valid_extensions']:
                if extension[0] != '.':
                    extension = '.' + extension
                valid_extensions.append(extension.lower())
        print('Done!')

        if debug:
            print('Valid extensions:')
            print('First 5 items: ')
            print(valid_extensions[:5])
            print(str(len(valid_extensions)) + ' loaded in total')
            print('')

        print('Scanning user binaries...')
        filter_binaries = True
        try:
            if self.prefs['filter_binaries'] == False:
                filter_binaries = False
        except:
            pass

        binaries = self.scan_binaries(filter_binaries)
        print('Done!')

        if debug:
            print('Valid binaries:')
            print('First 5 items: ')
            print(binaries[:5])
            print(str(len(binaries)) + ' loaded in total')
            print('')
        
        print('Loading the list of indexed folders...')
        
        watch_folders = []
        if 'watch_folders' in self.prefs:
            watch_folders = self.prefs['watch_folders']
        watch_folders = map(lambda x: x.replace('~', os.path.expanduser('~')), watch_folders)
        print('Done!')

        if debug:
            print('Watch folders:')
            print('First 5 items: ')
            print(watch_folders[:5])
            print(str(len(watch_folders)) + ' loaded in total')
            print('')

        print('Loading the list of folders to be excluded from the index...')
        
        ignore_folders = []

        if 'ignore_folders' in self.prefs:
            for exclude_folder in self.prefs['ignore_folders']:
                ignore_folders.append(exclude_folder.replace('~', os.path.expanduser('~')))

        print('Done!')

        if debug:
            print('Excluded folders:')
            print('First 5 items: ')
            print(ignore_folders[:5])
            print(str(len(ignore_folders)) + ' ignore_folders loaded in total')
            print('')

        filenames = []
        foldernames = []

        follow_symlinks = False
        try:
            if 'follow_symlinks' in self.prefs:
                follow_symlinks = self.prefs['follow_symlinks']
        except:
            pass

        if debug:
            if follow_symlinks:
                print('Indexing will not follow linked folders')
            else:
                print('Indexing will follow linked folders')

        print('Scanning files and folders, this may take a while...')
        print('')

        for watchdir in watch_folders:
            for root, dirs , files in os.walk(watchdir, followlinks=follow_symlinks):

                dirs[:] = [d for d in dirs if os.path.join(root,d) not in ignore_folders]

                if root.find('/.')  == -1:
                    for name in files:
                        if not name.startswith('.'):
                                if os.path.splitext(name)[1].lower() in valid_extensions:
                                    print('\rScanning: ' + root.strip()[0:70]),
                                    for i in range(70-len(root[0:70])):
                                        print (' '),
                                    filenames.append(os.path.join(root,name))
                    for name in dirs:
                        if not name.startswith('.'):
                            foldernames.append(os.path.join(root,name))

        print('\rDone scanning files and folders')
        foldernames = list(filter(lambda x: x not in ignore_folders, foldernames))

        if debug:
            print('Folders found:')
            print('First 5 items: ')
            print(foldernames[:5])
            print(str(len(foldernames)) + ' found in total')
            print('')

            print('Files found:')
            print('First 5 items: ')
            print(filenames[:5])
            print(str(len(filenames)) + ' found in total')
            print('')

        print('Loading manually added items from preferences file...')

        if 'include_items' in self.prefs:
            include_items = self.prefs['include_items']
        else:
            include_items = []
        print('Done!')

        if debug:
            print('Stored items:')
            print('First 5 items: ')
            print(include_items[:5])
            print(str(len(include_items)) + ' items loaded in total')
            print('')

        print('Ordering and combining results...')
        
        plugins = self.plugins_available()
        other = self.sort_shortest(include_items + binaries + foldernames + filenames)

        self.cache_save(other, file_cacheScanned)

        out = plugins
        out += other

        print('Done!')
        print('Cache building has finished.')
        print('')
        return out
