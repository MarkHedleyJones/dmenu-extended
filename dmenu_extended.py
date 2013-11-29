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
            print 'Loading plugin: ' + plugin
            __import__('plugins.' + plugin)
            exec('plugins_loaded.append({"filename": "' + plugin + '.py", "plugin": plugins.' + plugin + '.extension()})')

    return plugins_loaded


class dmenu(object):

    path_base = os.path.dirname(__file__)
    path_cache = path_base + '/cache.txt'
    path_store = path_base + '/store.txt'
    path_settings = path_base + '/settings.txt'

    dmenu_args = ['dmenu']
    bin_terminal = 'xterm'
    bin_filebrowser = 'nautilus'
    bin_webbrowser = 'firefox'

    plugins_loaded = False
    settings = False


    def titleise(self, title):
        out =  '--- ' + title + ' '
        for i in range(80 - len(title)):
            out += '-'
        return ['', out, '']

    def get_plugins(self, force=False):
        if force:
            reload(plugins)

        if force or self.plugins_loaded == False:
            self.plugins_loaded = load_plugins()
        return self.plugins_loaded


    def load_settings(self):
        if self.settings == False:
            with open(self.path_settings) as f:
                try:
                    self.settings = json.load(f)
                except:
                    print "Error parsing settings from json file"
                    sys.exit()

            if 'terminal' in self.settings:
                self.bin_terminal = self.settings['terminal']
            if 'filebrowser' in self.settings:
                self.bin_filebrowser = self.settings['filebrowser']
            if 'webbrowser' in self.settings:
                self.bin_webbrowser = self.settings['webbrowser']
            if 'dmenu_args' in self.settings:
                self.dmenu_args = ['dmenu'] + self.settings['dmenu_args']

    def connect_to(self, url):
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        return response

    def download_text(self, url):
        return self.connect_to(url).readlines()

    def download_json(self, url):
        return json.load(self.connect_to(url))

    def menu(self, items, prompt=False):
        self.load_settings()
        params = self.dmenu_args
        if prompt:
            params.append("-p")
            params.append(prompt)
        p = subprocess.Popen(params, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        if type(items) == str:
            out = p.communicate(items)[0]
        else:
            out = p.communicate("\n".join(items))[0]
        return out.strip('\n')


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
        return sorted(items, cmp=lambda x, y: len(x) - len(y))


    def open_url(self, url):
        print 'opening url: ' + url
        self.load_settings()
        os.system(self.bin_webbrowser + ' ' + url.replace(' ', '%20') + '&')


    def open_directory(self, path):
        print 'opening folder: ' + path
        self.load_settings()
        os.system(self.bin_filebrowser + ' "' + path + '"')


    def open_terminal(self, command, hold=False):
        self.load_settings()
        if hold:
            mid = ' -e sh -c "'
            command += '; echo \'\nCommand has finished!\n\nPress any key to close terminal\'; read var'
        else:
            mid = ' -e sh -c "'
        full = self.bin_terminal + mid + command + '"'
        os.system(full)


    def open_file(self, path):
        print "opening file: '" + path  + "'"
        os.system("xdg-open '" + path + "'")


    def execute(self, command):
        os.system(command + " &")


    def file_load(self, path):
        if os.path.isfile(path):
            with open(path, 'r') as f:
                out = f.readlines()
        else:
            out = []

        return map(lambda x: x.strip('\n'),out)


    def file_save(self, path, items):
        with open(path, 'w') as f:
            f.writelines(map(lambda x: x + '\n',items))


    def file_modify(self, path, item, add=True):
        tmp = file_load(path)
        if add:
            tmp.append(item)
        else:
            tmp.remove(item)
        self.file_save(path)

    def cache_regenerate(self):
        return self.cache_save(self.cache_build())

    def cache_save(self, items):
        try:
            with open(self.path_cache, 'w') as f:
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
                        print 'Non-printable characters detected in cache object: '
                        print 'Remedy: ' + item
                if clean:
                    tmp.append(item)
            if foundError:
                print ''
                print 'Performance affected while these items remain'
                print 'This items have been excluded from cache'
                print
                with open(self.path_cache, 'w') as f:
                    for item in tmp:
                        f.write(item+'\n')
                return 2
            else:
                print 'Unknown error saving data cache'
                return 0

    def cache_open(self):
        try:
            with open(self.path_cache, 'r') as f:
                return f.read()
        except:
            return False

    def cache_load(self):
        cache = self.cache_open()
        if cache == False:
            print 'Cache was not loaded'
            if self.cache_regenerate() == False:
                self.menu(['Error caching data'])
                sys.exit()
            else:
                cache = self.cache_open()

        return cache

    def scan_binaries(self, filter=False):
        out = []
        for prog in commands.getoutput("dmenu_path").split("\n"):
            if filter:
                if os.path.exists('/usr/share/applications/' + prog + '.desktop'):
                    if prog[:3] != 'gpk':
                        out.append(prog)
            else:
                out.append(prog)
        return out

    def cache_build(self):

        self.load_settings()

        tmp = self.settings['valid_extensions']
        valid_extensions = []
        for ext in tmp:
            ext = ext.strip()
            if ext[0] != '.':
                ext = '.' + ext
            valid_extensions.append(ext)

        print 'valid extensions:'
        print valid_extensions[:5]
        print str(len(valid_extensions)) + ' were loaded'
        print

        binaries = self.scan_binaries(True)

        print 'valid binaries:'
        print binaries[:5]
        print str(len(binaries)) + ' were loaded'
        print

        watch_folders = self.settings['watch_folders']

        watch_folders = map(lambda x: x.replace('~', os.path.expanduser('~')), watch_folders)


        print 'watch folders:'
        print watch_folders[:5]
        print str(len(watch_folders)) + ' were loaded'
        print

        filenames = []
        foldernames = []

        for watchdir in watch_folders:
            for root, dir , files in os.walk(watchdir):
                if root.find('/.')  == -1 :
                    for name in files:
                        if not name.startswith('.'):
                            if os.path.splitext(name)[1] in valid_extensions:
                                filenames.append(os.path.join(root,name))
                    for name in dir:
                        if not name.startswith('.'):
                            foldernames.append(os.path.join(root,name))

        print 'folders found:'
        print foldernames[:5]
        print str(len(foldernames)) + 'were found'
        print

        print 'files found:'
        print filenames[:5]
        print str(len(filenames)) + 'were found'
        print

        store = self.file_load(self.path_store)

        print 'stored commands:'
        print store[:5]
        print str(len(store)) + ' commands were loaded'
        print

        plugins = self.get_plugins()
        plugin_titles = []
        for plugin in plugins:
            plugin_titles.append(plugin['plugin'].title)

        print 'plugins loaded:'
        print plugin_titles[:5]
        print str(len(plugin_titles)) + ' were loaded'
        print

        user = self.sort_shortest(foldernames + filenames + store)
        bins = self.sort_shortest(binaries)
        plugins = self.sort_shortest(plugin_titles)


        out = plugins
        out += self.titleise('System binaries')
        out += bins
        out += self.titleise('Indexed files/folders')
        out += user

        return out


