import dmenu_extended
import sys
import os

class extension(dmenu_extended.dmenu):

    items = ['Rebuild cache',
             'Edit personal store',
             'Download new plugins',
             'Update dmenu-extended',
             'Remove existing plugins',
             'Edit dmenu-extended user settings',
             ]

    title = 'Menu configuration:'

    def rebuild_cache(self):
        print 'counting items in cache'
        cacheSize = len(self.cache_load())

        print 'rebuilding cache...'
        result = self.cache_save(self.cache_build())
        print result
        print 'cache built'

        print 'counting items in new cache'
        cacheSizeChange = len(self.cache_load()) - cacheSize
        print 'new cache size = ' + str(cacheSizeChange)

        response = []

        if result > 0:
            if cacheSizeChange == 1:
                status = 'One new item was added'
            elif cacheSizeChange == -1:
                status = 'One item was removed'
            elif cacheSizeChange > 0:
                status = str(cacheSizeChange) + ' items were added'
            elif cacheSizeChange < 0:
                status = str(abs(cacheSizeChange)) + ' items were removed'
            else:
                status = 'No new items were added'

            response.append('Cache updated successfully - ' + status)

            if result == 2:
                response.append('NOTICE: Performance issues were encoundered while caching data')

        else:
            response.append('Errors were encountered - the cache was not saved')

        self.menu(response)

    def rebuild_cache_plugin(self):
        self.plugins_loaded = self.get_plugins(True)
        self.cache_regenerate()

    def download_plugins(self):
        plugins = self.download_json('https://gist.github.com/markjones112358/7699540/raw/dmenu-extended-plugins.txt')

        items = []

        for plugin in plugins:
            items.append(plugin + ' - ' + plugins[plugin]['desc'])

        item = self.select(items, 'Select a plugin to install:')

        plugin_name = item.split(' - ')[0]
        plugin = plugins[plugin_name]
        plugin_source = self.download_text(plugin['url'])

        with open(self.path_base + '/plugins/' + plugin_name + '.py', 'w') as f:
            for line in plugin_source:
                f.write(line)

        self.rebuild_cache_plugin()

        self.menu(['Plugin dowloaded and installed successfully'])

    def remove_plugin(self):
        plugins = []
        for plugin in self.get_plugins():
            plugins.append(plugin["plugin"].title.replace(':','') + ' (' + plugin["filename"] + ')')
        pluginText = self.select(plugins, prompt='Plugin to remove:')
        if pluginText != -1:
            plugin = pluginText.split('(')[1].replace(')', '')
            path = self.path_base + '/plugins/' + plugin
            if os.path.exists(path):
                os.remove(path)
                self.rebuild_cache_plugin()
                self.menu(['Plugin "' + plugin + '" was removed.'])
            else:
                print 'Error - Plugin not found'
        else:
            print 'Selection was not understood'

    def update_dmenu_extended(self):
        self.open_terminal('cd ' + self.path_base + ' && git pull', True)


    def run(self, inputText):

        selectedIndex = self.select(self.items, "Action:", True)

        if selectedIndex == -1:
            sys.exit()

        if selectedIndex == 0:
            self.rebuild_cache()
        elif selectedIndex == 1:
            self.execute('xdg-open ' + self.path_base + '/store.txt')
        elif selectedIndex == 2:
            self.download_plugins()
        elif selectedIndex == 3:
            self.update_dmenu_extended()
        elif selectedIndex == 4:
            self.remove_plugin()
        elif selectedIndex == 5:
            self.execute('xdg-open ' + self.path_base + '/settings.txt')
        else:
            sys.exit()
