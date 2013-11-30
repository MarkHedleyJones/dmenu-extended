# -*- coding: utf8 -*-
import commands
import sys
import os
import subprocess
import json
import urllib2
import plugins

def load_plugins():

    plugins_loaded = []

    for plugin in plugins.__all__:
        if plugin != '__init__':
            print('Loading plugin: ' + plugin)
            __import__('plugins.' + plugin)
            exec('plugins_loaded.append({"filename": "' + plugin + '.py", "plugin": plugins.' + plugin + '.extension()})')

    return plugins_loaded


class dmenu(object):

    path_base = os.path.dirname(__file__)
    path_cache = path_base + '/cache.txt'
    path_preferences = path_base + '/user_preferences.txt'
    path_configuration = path_base + '/configuration.txt'

    dmenu_args = ['dmenu']
    bin_terminal = 'xterm'
    bin_filebrowser = 'nautilus'
    bin_webbrowser = 'firefox'

    submenu_indicator = '* '

    plugins_loaded = False
    configuration = False
    preferences = False

    def get_plugins(self, force=False):
        if force:
            reload(plugins)

        if force or self.plugins_loaded == False:
            self.plugins_loaded = load_plugins()
        return self.plugins_loaded

    def load_json(self, path):
        if os.path.exists(path):
            with open(path) as f:
                try:
                    return json.load(f)
                except:
                    print("Error parsing configuration from json file " + path)
                    return False
        else:
            print('Error opening json file ' + path)
            print('File does not exist')
            return False

    def save_json(self, path, items):
        with open(path, 'w') as f:
            json.dump(items, f, sort_keys=True, indent=4)
        return

    def load_configuration(self):
        if self.configuration == False:
            self.configuration = self.load_json(self.path_configuration)
            if self.configuration == False:
                self.configuration = []

            if 'terminal' in self.configuration:
                self.bin_terminal = self.configuration['terminal']
            if 'filebrowser' in self.configuration:
                self.bin_filebrowser = self.configuration['filebrowser']
            if 'webbrowser' in self.configuration:
                self.bin_webbrowser = self.configuration['webbrowser']
            if 'dmenu_args' in self.configuration:
                self.dmenu_args = ['dmenu'] + self.configuration['dmenu_args']
            if 'submenu_indicator' in self.configuration:
                self.submenu_indicator = self.configuration['submenu_indicator']

    def load_preferences(self):
        if self.preferences == False:
            preferences = self.load_json(self.path_preferences)
            print(preferences)
            if preferences != False:
                self.preferences = preferences
            else:
                self.preferences = []


    def connect_to(self, url):
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        return response

    def download_text(self, url):
        return self.connect_to(url).readlines()

    def download_json(self, url):
        return json.load(self.connect_to(url))

    def menu(self, items, prompt=None):
        self.load_configuration()

        params = []
        params += self.dmenu_args
        if prompt is not None:
            params += ["-p", prompt]

        p = subprocess.Popen(params, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        if type(items) == str:
            out = p.communicate(items)[0]
        else:
            out = p.communicate("\n".join(items))[0]
        return out.strip('\n')


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
        return sorted(items, cmp=lambda x, y: len(x) - len(y))


    def open_url(self, url):
        print('opening url: ' + url)
        self.load_configuration()
        os.system(self.bin_webbrowser + ' ' + url.replace(' ', '%20') + '&')


    def open_directory(self, path):
        print('opening folder: ' + path)
        self.load_configuration()
        os.system(self.bin_filebrowser + ' "' + path + '"')


    def open_terminal(self, command, hold=False):
        self.load_configuration()
        if hold:
            mid = ' -e sh -c "'
            command += '; echo \'\nCommand has finished!\n\nPress any key to close terminal\'; read var'
        else:
            mid = ' -e sh -c "'
        full = self.bin_terminal + mid + command + '"'
        os.system(full)


    def open_file(self, path):
        print("opening file: '" + path  + "'")
        os.system("xdg-open '" + path + "'")


    def execute(self, command, fork=None):
        if fork is not None:
            if fork == False:
                extra = ''
            else:
                extra = ' &'
        else:
            extra = ' &'
        os.system(command + extra)


    def cache_regenerate(self):
        return self.cache_save(self.cache_build())

    def cache_save(self, items):
        try:
            with open(self.path_cache, 'wb') as f:
                for item in items:
                    f.write(item+'\n')
            return 1
        except:
            import string
            tmp = []
            foundError = False
            for item in items:
                clean = True
                for char in item:
                    if char not in string.printable:
                        clean = False
                        foundError = True
                        print('Non-printable characters detected in cache object: ')
                        print('Remedy: ' + item)
                if clean:
                    tmp.append(item)
            if foundError:
                print()
                print('Performance affected while these items remain')
                print('This items have been excluded from cache')
                print()
                with open(self.path_cache, 'wb') as f:
                    for item in tmp:
                        f.write(item+'\n')
                return 2
            else:
                print('Unknown error saving data cache')
                return 0

    def cache_open(self):
        try:
            with open(self.path_cache, 'rb') as f:
                return f.read()
        except:
            return False

    def cache_load(self):
        cache = self.cache_open()
        if cache == False:
            print('Cache was not loaded')
            if self.cache_regenerate() == False:
                self.menu(['Error caching data'])
                sys.exit()
            else:
                cache = self.cache_open()

        return cache

    def command_output(self, command):
        if type(command) == str:
            command = command.split(' ')
        print command
        handle = subprocess.Popen(command, stdout=subprocess.PIPE)
        return handle.communicate()[0].split('\n')

    def scan_binaries(self, filter=False):
        out = []
        for binary in self.command_output("dmenu_path"):
            if filter:
                if os.path.exists('/usr/share/applications/' + binary + '.desktop'):
                    if binary[:3] != 'gpk':
                        out.append(binary)
            else:
                out.append(binary)
        return out

    def cache_build(self, debug=False):

        self.load_configuration()
        self.load_preferences()


        valid_extensions = []
        if 'valid_extensions' in self.preferences:
            for extension in self.preferences['valid_extensions']:
                if extension[0] != '.':
                    extension = '.' + extension
                valid_extensions.append(extension)

        if debug:
            print('valid extensions:')
            print(valid_extensions[:5])
            print(str(len(valid_extensions)) + ' were loaded')
            print()

        binaries = self.scan_binaries(True)

        if debug:
            print('valid binaries:')
            print(binaries[:5])
            print(str(len(binaries)) + ' were loaded')
            print()

        watch_folders = []
        if 'watch_folders' in self.preferences:
            watch_folders = self.preferences['watch_folders']
        watch_folders = map(lambda x: x.replace('~', os.path.expanduser('~')), watch_folders)

        if debug:
            print('watch folders:')
            print(watch_folders[:5])
            print(str(len(watch_folders)) + ' were loaded')
            print()

        filenames = []
        foldernames = []

        exclude_folders = []
        if 'exclude_folders' in self.preferences:
            exclude_folders = self.preferences['exclude_folders']
        exclude_folders = map(lambda x: x.replace('~', os.path.expanduser('~')), exclude_folders)

        if debug:
            print('excluded folders:')
            print(exclude_folders[:5])
            print(str(len(exclude_folders)) + ' exclude_folders were loaded')
            print()

        for watchdir in watch_folders:
            for root, dir , files in os.walk(watchdir):
                if root.find('/.')  == -1:
                    for name in files:
                        if not name.startswith('.'):
                                if os.path.splitext(name)[1] in valid_extensions:
                                    filenames.append(os.path.join(root,name))
                    for name in dir:
                        if not name.startswith('.'):
                            foldernames.append(os.path.join(root,name))

        foldernames = filter(lambda x: x not in exclude_folders, foldernames)

        if debug:
            print('folders found:')
            print(foldernames[:5])
            print(str(len(foldernames)) + 'were found')
            print()

            print('files found:')
            print(filenames[:5])
            print(str(len(filenames)) + 'were found')
            print()

        if 'include_items' in self.preferences:
            include_items = self.preferences['include_items']
        else:
            include_items = []

        if debug:
            print('stored items:')
            print(include_items[:5])
            print(str(len(include_items)) + ' items were loaded')
            print()

        plugins = self.get_plugins()
        plugin_titles = []
        for plugin in plugins:
            if hasattr(plugin['plugin'], 'is_submenu') and plugin['plugin'].is_submenu:
                plugin_titles.append(self.submenu_indicator + plugin['plugin'].title)
            else:
                plugin_titles.append(plugin['plugin'].title)

        if debug:
            print('plugins loaded:')
            print(plugin_titles[:5])
            print(str(len(plugin_titles)) + ' were loaded')
            print()

        user = self.sort_shortest(foldernames + filenames + include_items)
        bins = self.sort_shortest(binaries)
        plugins = self.sort_shortest(plugin_titles)

        out = plugins
        out += bins
        out += user

        return out


