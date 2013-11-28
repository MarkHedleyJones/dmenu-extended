import commands
import sys
import os
import subprocess
import numpy as np
import json

def load_plugins():
    import plugins

    plugins_loaded = []

    for plugin in plugins.__all__:
        if plugin != '__init__':
            print 'Loading plugin: ' + plugin
            __import__('plugins.' + plugin)
            exec('plugins_loaded.append(plugins.'+plugin+'.extension())')

    return plugins_loaded


class dmenu(object):

    path_base = os.path.dirname(__file__)
    path_cache = path_base + '/cache.npy'
    path_store = path_base + '/store.txt'
    path_settings = path_base + '/settings.txt'

    bin_dmenu = 'dmenu'
    bin_terminal = 'urxvt'
    bin_filebrowser = 'pcmanfm'
    bin_webbrowser = 'firefox'

    plugins_loaded = False
    settings = False

    def __init__(self,
                 terminal='urxvt',
                 filebrowser='pcmanfm',
                 webbrowser='firefox'):

        self.bin_terminal = terminal
        self.bin_filebrowser = filebrowser
        self.bin_webbrowser = webbrowser


    def titleise(self, title):
        out =  '--- ' + title + ' '
        for i in range(80 - len(title)):
            out += '-'
        return ['', out, '']

    def get_plugins(self):
        if self.plugins_loaded == False:
            self.plugins_loaded = load_plugins()
        return self.plugins_loaded


    def load_settings(self):
        with open(self.path_settings) as f:
            try:
                self.settings = json.load(f)
            except:
                print "Error parsing settings from json file"
                sys.exit()

        return self.settings


    def menu(self, items, prompt=False):
        params = [
            self.bin_dmenu,
            "-b",
            "-i",
            "-nf",
            "#888888",
            "-nb",
            "#1D1F21",
            "-sf",
            "#ffffff",
            "-sb",
            "#1D1F21",
            "-fn",
            "-*-terminus-medium-r-*-*-16-*-*-*-*-*-*-*",
            "-l",
            "30"]
        if prompt:
            params.append("-p")
            params.append(prompt)

        p = subprocess.Popen(params, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out = p.communicate("\n".join(items))[0]
        return out.strip('\n')

    def sort_shortest(self, items):
        return sorted(items, cmp=lambda x, y: len(x) - len(y))

    def open_url(self, url):
        os.system(self.bin_webbrowser + ' ' + url.replace(' ', '%20') + '&')

    def open_directory(self, path):
        os.system(self.bin_filebrowser + ' ' + path)

    def open_terminal(self, command, hold=False):
        if hold:
            mid = ' -e sh -c "'
            command += '; echo \'\nCommand has finished!\n\nPress any key to close terminal\'; read var'
        else:
            mid = ' -e sh -c "'
        full = self.bin_terminal + mid + command + '"'
        os.system(full)

    def open_file(self, path):
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


    def cache_save(self, items):
        try:
            out = np.array(items, dtype='S 200')
            out.tofile(self.path_cache)
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
                out = np.array(tmp, dtype='S 200')
                out.tofile(self.path_cache)
                return 2
            else:
                print 'Unknown error saving data cache'
                return 0


    def cache_load(self):
        try:
            out = np.fromfile(self.path_cache, dtype='S 200')
        except:
            print 'Cache was not loaded'
            out = self.cache_build()
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

        binaries = []

        for prog in commands.getoutput("dmenu_path").split("\n"):
            if os.path.exists('/usr/share/applications/' + prog + '.desktop'):
                if prog[:3] != 'gpk':
                    binaries.append(prog)

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
            plugin_titles.append(plugin.title)

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


