# -*- coding: utf8 -*-
from __future__ import unicode_literals
import sys
import os
import subprocess
import signal
import json

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
        "py",                           # Python script
        "svg",                          # Vector graphics
        "pdf",                          # Portable document format
        "txt",                          # Plain text
        "png",                          # Image file
        "jpg",                          # Image file
        "gif",                          # Image file
        "php",                          # PHP source-code
        "tex",                          # LaTeX document
        "odf",                          # Open document format
        "ods",                          # Open document spreadsheet
        "avi",                          # Video file
        "mpg",                          # Video file
        "mp3",                          # Music file
        "lyx",                          # Lyx document
        "bib",                          # LaTeX bibliograpy
        "iso",                          # CD image
        "ps",                           # Postscript document
        "zip",                          # Compressed archive
        "xcf",                          # Gimp image format
        "doc",                          # Microsoft document format
        "docx"                          # Microsoft document format
        "xls",                          # Microsoft spreadsheet format
        "xlsx",                         # Microsoft spreadsheet format
        "md",                           # Markup document
        "sublime-project"               # Project file for sublime
    ],
    "watch_folders": ["~/"],            # Base folders through which to search
    "follow_symlinks": False,           # Follow links to other locations
    "ignore_folders": [],               # Folders to exclude from the search
    "scan_hidden_folders": False,       # Enter hidden folders while scanning for items
    "include_hidden_files": False,      # Include hidden files in the cache
    "include_hidden_folders": False,    # Include hidden folders in the cache
    "include_items": [],                # Extra items to display - manually added
    "exclude_items": [],                # Items to hide - manually hidden
    "filter_binaries": True,            # Only include binaries that have a .desktop file
    "menu": 'dmenu',                    # Executable for the menu
    "menu_arguments": [
        "-b",                           # Place at bottom of screen
        "-i",                           # Case insensitive searching
        "-nf",                          # Element foreground colour
        "#888888",
        "-nb",                          # Element background colour
        "#1D1F21",
        "-sf",                          # Selected element foreground colour
        "#ffffff",
        "-sb",                          # Selected element background colour
        "#1D1F21",
        "-fn",                          # Font and size
        "-*-terminus-medium-*-*-*-14-*-*-*-*-*-*-*",
        "-l",                           # Number of lines to display
        "20"
    ],
    "fileopener": "xdg-open",           # Program to handle opening files
    "filebrowser": "xdg-open",          # Program to handle opening paths
    "webbrowser": "xdg-open",           # Program to hangle opening urls
    "terminal": "xterm",                # Terminal
    "indicator_submenu": "->",          # Symbol to indicate a submenu item
    "indicator_edit": "*",              # Symbol to indicate an item will launch an editor
    "indicator_alias": "#"              # Symbol to indecate an aliased command
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

    # If relevant binaries exist, swap them out for the more appropriate items
    if os.path.exists('/usr/bin/gnome-open'):
        default_prefs['fileopener'] = 'gnome-open'
        default_prefs['webbrowser'] = 'gnome-open'
        default_prefs['filebrowser'] = 'gnome-open'
    if os.path.exists('/usr/bin/gnome-terminal'):
        default_prefs['terminal'] = 'gnome-terminal'
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
    plugins_loaded = [{"filename": "dmenuExtended_settings.py",
                       "plugin": extension()}]
    for plugin in plugins.__all__:
        if plugin not in ['__init__', 'dmenuExtended_settings.py']:
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


    def system_path(self):
        """
        Array containing system paths
        """
        path = str(subprocess.check_output("echo $PATH", shell=True))
        path = path.replace('\\n','').replace('b\'','').replace('\'','')
        path = list(set(path.split(':'))) # Split and remove duplicates
        return path


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
                    self.prefs = default_prefs
                    option = self.prefs['indicator_edit'] +" Edit file manually"
                    response = self.menu("There is an error opening " + path + "\n" + option)
                    if response == option:
                        self.open_file(path)
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
        self.save_json(file_prefs, self.prefs)


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

        if sys.version_info >= (3,0):
            items = items.encode('utf-8')
        elif type(items) != str:
            items = items.encode('utf-8')

        out = p.communicate(items)[0]

        if out.strip() == '':
            sys.exit()
        else:
            return out.decode().strip('\n')


    def select(self, items, prompt=False, numeric=False):
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
                f.write('echo "\n\nPress enter to exit";')
                f.write('read var;')

        os.chmod(file_shCmd, 0o744)
        os.system(self.prefs['terminal'] + ' -e ' + file_shCmd)


    def open_file(self, path):
        self.load_preferences()
        print('Opening file with command: ' + self.prefs['fileopener'] + " '" + path + "'")
        exit_code = os.system(self.prefs['fileopener'] + " '" + path + "'")
        if exit_code is not 0:
            open_failure = False
            offer = None
            if exit_code == 256 and self.prefs['fileopener'] == 'gnome-open':
                open_failure = True
                offer = 'xdg-open'
            elif exit_code == 4 and self.prefs['fileopener'] == 'xdg-open':
                open_failure = True
            if open_failure:
                mimetype = str(self.command_output('xdg-mime query filetype ' + path)[0])
                message = ["Error: " + self.prefs['fileopener'] + " reports no application is associated with this filetype (MIME type: " + mimetype + ")"]
                if offer is not None:
                    option = "Try opening with " + offer + "?"
                message.append(option)

                if self.menu(message) == option:
                    self.prefs['fileopener'] = offer
                    self.open_file(path)


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
            self.message_open('building cache...\nThis may take a while (press enter to run in background).')
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
        for path in self.system_path():
            if os.path.exists(path):
                for binary in os.listdir(path):
                    if filter_binaries:
                        if os.path.exists('/usr/share/applications/' + binary + '.desktop'):
                            if binary[:3] != 'gpk':
                                out.append(binary)
                    else:
                        out.append(binary)
            else:
                print(str(path) + ' is in the system path but does not exist')

        return out


    def plugins_available(self, debug=False):
        self.load_preferences()
        print('Loading available plugins...')

        plugins = self.get_plugins(True)
        plugin_titles = []
        for plugin in plugins:
            if hasattr(plugin['plugin'], 'is_submenu') and plugin['plugin'].is_submenu:
                plugin_titles.append(self.prefs['indicator_submenu'] + ' ' + plugin['plugin'].title)
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
                if extension == '*':
                    valid_extensions = True
                    break
                elif extension == '':
                    valid_extensions.append('')
                elif extension[0] != '.':
                    extension = '.' + extension
                valid_extensions.append(extension.lower())

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

        if debug:
            print('Done!')
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

        if debug:
            print('Done!')
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

        if debug:
            print('Done!')
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

        for watchdir in watch_folders:
            for root, dirs , files in os.walk(watchdir, followlinks=follow_symlinks):
                dirs[:] = [d for d in dirs if os.path.join(root,d) not in ignore_folders]

                if self.prefs['scan_hidden_folders'] or root.find('/.')  == -1:
                    for name in files:
                        if self.prefs['include_hidden_files'] or name.startswith('.') == False:
                            if valid_extensions == True or os.path.splitext(name)[1].lower() in valid_extensions:
                                filenames.append(os.path.join(root,name))
                    for name in dirs:
                        if self.prefs['include_hidden_folders'] or name.startswith('.') == False:
                            foldernames.append(os.path.join(root,name))

        foldernames = list(filter(lambda x: x not in ignore_folders, foldernames))

        if debug:
            print('Done!')
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
            include_items = []
            for item in self.prefs['include_items']:
                if type(item) == list:
                    if len(item) > 1:
                        include_items.append(self.prefs['indicator_alias'] + ' ' + item[0])
                    else:
                        if debug:
                            print("There are aliased items in the configuration with no command.")
                else:
                    include_items.append(item)
        else:
            include_items = []

        if debug:
            print('Done!')
            print('Stored items:')
            print('First 5 items: ')
            print(include_items[:5])
            print(str(len(include_items)) + ' items loaded in total')
            print('')
            print('Ordering and combining results...')

        plugins = self.plugins_available()
        other = self.sort_shortest(include_items + binaries + foldernames + filenames)

        if 'exclude_items' in self.prefs:
            for item in self.prefs['exclude_items']:
                try:
                    other.remove(item)
                except ValueError:
                    pass

        self.cache_save(other, file_cacheScanned)

        out = plugins
        out += other

        if debug:
            print('Done!')
            print('Cache building has finished.')
            print('')

        return out


class extension(dmenu):

    title = 'Menu configuration'
    is_submenu = True

    def __init__(self):
        self.load_preferences()

    plugins_index_url = 'https://gist.github.com/markjones112358/7699540/raw/dmenu-extended-plugins.txt'

    def rebuild_cache(self):
        print('Counting items in original cache')
        cacheSize = len(self.cache_load().split("\n"))

        print('Rebuilding the cache...')
        result = self.cache_regenerate()
        print('Cache built')

        print('Counting items in new cache')
        newSize = len(self.cache_load().split("\n"))
        print('New cache size = ' + str(newSize))
        cacheSizeChange = newSize - cacheSize
        if cacheSizeChange != 0:
            print('This differs from original by ' + str(cacheSizeChange) + ' items')
        else:
            print('Cache size did not change')

        response = []

        if cacheSizeChange != 0:
            if cacheSizeChange == 1:
                status = 'one new item was added.'
            elif cacheSizeChange == -1:
                status = 'one item was removed.'
            elif cacheSizeChange > 0:
                status = str(cacheSizeChange) + ' items were added.'
            elif cacheSizeChange < 0:
                status = str(abs(cacheSizeChange)) + ' items were removed.'
            else:
                status = 'No new items were added'

            response.append('Cache updated successfully; ' + status)

            if result == 2:
                response.append('NOTICE: Performance issues were encountered while caching data')

        else:
            response.append('Cache rebuilt; its size did not change.')

        response.append('The cache contains ' + str(cacheSize) + ' items.')

        self.menu(response)


    def rebuild_cache_plugin(self):
        self.plugins_loaded = self.get_plugins(True)
        self.cache_regenerate()


    def download_plugins(self):
        self.message_open('Downloading a list of plugins...')

        try:
            plugins = self.download_json(self.plugins_index_url)
        except:
            self.message_close()
            self.menu(["Error: Could not connect to plugin repository.",
                       "Please check your internet connection and try again."])
            sys.exit()

        items = []

        substitute = ('dmenuExtended_', '')

        installed_plugins = self.get_plugins()
        installed_pluginFilenames = []

        for tmp in installed_plugins:
            installed_pluginFilenames.append(tmp['filename'])

        for plugin in plugins:
            if plugin + '.py' not in installed_pluginFilenames:
                items.append(plugin.replace(substitute[0], substitute[1]) + ' - ' + plugins[plugin]['desc'])

        self.message_close()

        if len(items) == 0:
            self.menu(['There are no new plugins to install'])
        else:
            item = substitute[0] + self.select(items, 'Install:')

            if item != -1:
                self.message_open("Downloading selected plugin...")
                plugin_name = item.split(' - ')[0]
                plugin = plugins[plugin_name]
                plugin_source = self.download_text(plugin['url'])

                with open(path_plugins + '/' + plugin_name + '.py', 'w') as f:
                    for line in plugin_source:
                        f.write(line)

                self.get_plugins(True)
                self.message_close()
                self.message_open("Rebuilding plugin cache")
                self.plugins_available()
                self.message_close()

                self.menu(['Plugin downloaded and installed successfully'])

                print("Plugins available:")
                for plugin in self.plugins_available():
                    print(plugin)


    def installed_plugins(self):
        plugins = []
        for plugin in self.get_plugins():
            plugins.append(plugin["plugin"].title.replace(':','') + ' (' + plugin["filename"] + ')')
        return plugins


    def remove_plugin(self):
        plugins = self.installed_plugins()
        pluginText = self.select(plugins, prompt='Plugin to remove:')
        if pluginText != -1:
            plugin = pluginText.split('(')[1].replace(')', '')
            path = path_plugins + '/' + plugin
            if os.path.exists(path):
                os.remove(path)
                self.menu(['Plugin "' + plugin + '" was removed.'])
                print("Plugins available:")
                for plugin in self.plugins_available():
                    print(plugin)
            else:
                print('Error - Plugin not found')
        else:
            print('Selection was not understood')


    def update_plugins(self):
        self.message_open('Checking for plugin updates...')
        plugins_here = list(map(lambda x: x['filename'].split('.')[0], self.get_plugins()))
        plugins_here.remove('dmenuExtended_settings')
        plugins_there = self.download_json(self.plugins_index_url)
        updated = []
        for here in plugins_here:
            for there in plugins_there:
                if there == here:
                    there_sha = plugins_there[there]['sha1sum']
                    here_sha = self.command_output("sha1sum " + path_plugins + '/' + here + '.py')[0].split()[0]
                    print('Checking ' + here)
                    print('Local copy has sha of ' + here_sha)
                    print('Remote copy has sha of ' + there_sha)
                    if there_sha != here_sha:
                        sys.stdout.write("Hashes do not match, updating...\n")
                        if os.path.exists('/tmp/' + there + '.py'):
                            os.remove('/tmp/' + there + '.py')
                        os.system('wget ' + plugins_there[there]['url'] + ' -P /tmp')
                        download_sha = self.command_output("sha1sum /tmp/" + here + '.py')[0].split()[0]
                        if download_sha != there_sha:
                            print('Downloaded version of ' + there + ' does not verify against package manager sha1sum key')
                            print('SHA1SUM of downloaded version = ' + download_sha)
                            print('SHA1SUM specified by package manager = ' + there_sha)
                            print('Plugin not updated')
                        else:
                            os.remove(path_plugins + '/' + here + '.py')
                            os.system('mv /tmp/' + here + '.py ' + path_plugins + '/' + here + '.py')
                            print('Done!')
                            updated += [here]
                    else:
                        print(here + 'is up-to-date')
        self.message_close()
        if len(updated) == 0:
            self.menu(['There are no new updates for installed plugins'])
        elif len(updated) == 1:
            self.menu([updated[0] + ' was updated to the latest version'])
        else:
            self.menu(['The following plugins were updated:'] + updated)


    def run(self, inputText):
        items = ['Rebuild cache',
                 self.prefs['indicator_submenu'] + ' Download new plugins',
                 self.prefs['indicator_submenu'] + ' Remove existing plugins',
                 self.prefs['indicator_edit'] + ' Edit menu preferences',
                 'Update installed plugins']

        selectedIndex = self.select(items, "Action:", numeric=True)

        if selectedIndex != -1:
            if selectedIndex == 0:
                self.rebuild_cache()
            elif selectedIndex == 1:
                self.download_plugins()
            elif selectedIndex == 2:
                self.remove_plugin()
            elif selectedIndex == 3:
                self.open_file(file_prefs)
                self.plugins_available() # Refresh the plugin cache
            elif selectedIndex == 4:
                self.update_plugins()


def handle_command(d, out):
    if out[-1] == ';':
        terminal_hold = False
        if out[-2] == ';':
            terminal_hold = True
        for command in out.split('&&'):
            if command.find('/') != -1:
                d.open_terminal("-cd " + command.replace(';',''),
                                direct=True,
                                hold=terminal_hold)
            else:
                d.open_terminal(command.replace(';',''),
                                hold=terminal_hold)

    elif out[:7] == 'http://' or out[:8] == 'https://':
        d.open_url(out)

    elif out.find('/') != -1:
        if out.find(' ') != -1:
            parts = out.split(' ')
            if parts[0] in d.scan_binaries():
                d.execute(out)
            else:
                if os.path.isdir(out):
                    d.open_directory(out)
                else:
                    d.open_file(out)
        else:
            if os.path.isdir(out):
                d.open_directory(out)
            else:
                d.open_file(out)
    else:
        d.execute(out)


def run():
    d = dmenu()
    cache = d.cache_load()
    out = d.menu(cache,'Open:').strip()


    if len(out) > 0:
        # Check if the action relates to a plugin
        plugins = load_plugins()
        plugin_hook = False
        for plugin in plugins:
            if hasattr(plugin['plugin'], 'is_submenu') and plugin['plugin'].is_submenu == True:
                pluginTitle = d.prefs['indicator_submenu'] + ' ' + plugin['plugin'].title.strip()
            else:
                pluginTitle = plugin['plugin'].title.strip()

            if out[:len(pluginTitle)] == pluginTitle:
                plugin_hook = plugin["plugin"]

        # Check for plugin call
        if plugin_hook != False:
            plugin_hook.run(out[len(pluginTitle):])
        else:
            # Check for command alias
            alias = d.prefs['indicator_alias']
            if out[0:len(alias)] == alias:
                command_key = out[len(alias):].lstrip()
                for item in [x for x in d.prefs['include_items'] if type(x) == list]:
                    if item[0] == command_key:
                        out = item[1]
            else:
                # Check for store modifications
                # Dont allow command aliases that add new commands
                if out[0] in "+-":

                    action = out[0]
                    out = out[1:]
                    aliased = False
                    # Check for aliased command
                    if out.find(d.prefs['indicator_alias']) != -1 and action == '+':
                        print("aliased command to add")
                        aliased = True
                        tmp = out.split(d.prefs['indicator_alias'])
                        # out = [tmp[1].lstrip(), tmp[0].rstrip()]

                        command = tmp[0].rstrip()
                        if command is not '':
                            out = tmp[1].lstrip() + ' (' + command.replace(';', '') + ')'
                        else:
                            out = tmp[1].lstrip()

                        if len(out) == 0:
                            item = command
                        else:
                            item = [out, command]
                    elif out[:len(d.prefs['indicator_alias'])] == d.prefs['indicator_alias']:
                        item = out[len(d.prefs['indicator_alias']):].lstrip()
                        aliased = True
                        print("Remove aliased indicator")
                    else:
                        item = out

                    print("The item is:")
                    print(item)

                    found_in_store = False
                    for store_item in d.prefs['include_items']:
                        print("is " + str(store_item) + " = " + str(item) + " ?")
                        if type(store_item) == list and out == store_item[0]:
                            found_in_store = True
                            break;
                        elif item == store_item:
                            found_in_store = True
                            break;

                    if found_in_store:
                        print("Yes")
                    else:
                        print("No")

                    if action == '+' and found_in_store:
                        option = d.prefs['indicator_submenu'] + " Remove from store"
                        answer = d.menu("Item '" + str(item) + "' already in store\n"+option)
                        if answer != option:
                            sys.exit()
                        action = '-'
                    elif action == '-' and found_in_store == False:
                        option = d.prefs['indicator_submenu'] + " Add to store"
                        answer = d.menu("Item '" + (item) + "' was not found in store\n"+option)
                        if answer != option:
                            sys.exit()
                        action = '+'

                    print("These are the stored items")
                    print(d.prefs['include_items'])

                    if action == '+':
                        d.prefs['include_items'].append(item)
                    elif action == '-':
                        if aliased:
                            to_remove = None
                            for include_item in d.prefs['include_items']:
                                if include_item[0] == out:
                                    to_remove = include_item
                            if to_remove is not None:
                                print("Item found and is")
                                print(to_remove)
                                d.prefs['include_items'].remove(to_remove)
                            else:
                                print("Couldn't remove the item (item could not be located)")
                        else:
                            d.prefs['include_items'].remove(item)
                    else:
                        d.message_close()
                        d.menu("An error occured while servicing your request.\nYou may need to delete your configuration file.")
                        sys.exit()

                    d.save_preferences()

                    # Recreate the cache

                    cache_scanned = d.cache_open(file_cacheScanned)[:-1]

                    if cache_scanned == False:
                        d.cache_regenerate()
                        d.message_close()
                        sys.exit()
                    else:
                        cache_scanned = cache_scanned.split("\n")

                    if action == '+':
                        print("Adding item to store: " + out)
                        d.message_open("Adding item to store: " + out)
                        if aliased:
                            cache_scanned = [d.prefs['indicator_alias'] + ' ' + out] + cache_scanned
                        else:
                            cache_scanned = [out] + cache_scanned
                        cache_scanned.sort(key=len)
                    else:
                        if aliased:
                            to_remove = d.prefs['indicator_alias'] + ' ' + out
                            print("Removing item from store: " + to_remove)
                        else:
                            to_remove = out
                        d.message_open("Removing item from store: " + to_remove)
                        try:
                            cache_scanned.remove(to_remove)
                        except ValueError:
                            print("Couldnt actually remove item from the cache")

                    d.cache_save(cache_scanned,file_cacheScanned)

                    d.message_close()
                    if action == '+':
                        if aliased == True:
                            message = "New item (" + command + " aliased as '" + out + "') added to cache."
                        else:
                            message = "New item (" + out + ") added to cache."
                    else:
                        message = "Existing item (" + out + ") removed from cache."

                    d.menu(message)
                    sys.exit()

            # Detect if the command is a web address and pass to handle_command
            if out[:7] == 'http://' or out[:8] == 'https://':
                handle_command(d, out)
            elif out.find(':') != -1:
                tmp = out.split(':')
                if len(tmp) != 2:
                    print('Input command not understood')
                    sys.exit()
                else:
                    cmds = list(map(lambda x: x.strip(), tmp))

                run_withshell = False
                shell_hold = False
                if cmds[0][-1] == ';':
                    if cmds[0][-2] == ';':
                        shell_hold = True
                        print('Will hold')
                    else:
                        print('Wont hold')
                    cmds[0] = cmds[0].replace(';','')
                    run_withshell = True

                if cmds[0] == '':
                    items = list(filter(lambda x: x.find(cmds[1]) != -1, cache.split('\n')))
                    item = d.menu(items)
                    handle_command(d, item)
                elif cmds[0] in d.scan_binaries():
                    print('Item[0] (' + cmds[0] + ') found in binaries')
                    # Get paths from cache
                    items = list(filter(lambda x: x.find('/') != -1, cache.split('\n')))
                    # If extension passed, filter by this
                    if cmds[1] != '':
                        items = list(filter(lambda x: x.find(cmds[1]) != -1, items))
                    filename = d.menu(items)
                    filename = os.path.expanduser(filename)
                    command = cmds[0] + " '" + filename + "'"
                    if run_withshell:
                        d.open_terminal(command, shell_hold)
                    else:
                        d.execute(command)
                elif cmds[0].find('/') != -1:
                    # Path came first, assume user wants of open it with a bin
                    if cmds[1] != '':
                        command = cmds[1] + " '" + os.path.expanduser(cmds[0]) + "'"
                    else:
                        binary = d.menu(d.scan_binaries())
                        command = binary + " '" + os.path.expanduser(cmds[0]) + "'"
                    d.execute(command)
                else:
                    d.menu(["Cant find " + cmds[0] + ", is it installed?"])
                    print('Input command not understood')

                sys.exit()

            if out == "rebuild cache":
                result = d.cache_regenerate()
                if result == 0:
                    d.menu(['Cache could not be saved'])
                elif result == 2:
                    d.menu(['Cache rebuilt','Performance issues were detected - some paths contained invalid characters'])
                else:
                    d.menu(['Success!'])

            else:
                handle_command(d, out)

if __name__ == "__main__":
    run()