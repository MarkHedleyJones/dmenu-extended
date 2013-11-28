import dmenu_extended
import sys

class extension(dmenu_extended.dmenu):

    items = ['Rebuild cache',
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
                status = str(cacheSizeChange) + ' items were removed'
            else:
                status = 'No new items were added'

            response.append('Cache updated successfully - ' + status)

            if result == 2:
                response.append('NOTICE: Performance issues were encoundered while caching data')

        else:
            response.append('Errors were encountered - the cache was not saved')

        self.menu(response)


    def run(self, inputText):

        itemText = self.menu(self.items)

        selectedIndex = False

        for i, item in enumerate(self.items):
            if itemText.find(item) != -1:
                selectedIndex = i

        if type(selectedIndex) == False:
            sys.exit()

        if selectedIndex == 0:
            self.rebuild_cache()
        elif selectedIndex == 1:
            self.menu(['Not implemented yet - coming soon'])
        elif selectedIndex == 3:
            plugins = []
            for plugin in self.get_plugins():
                plugins.append(plugin.title.replace(':',''))
            self.menu(plugins,'Plugin to remove:')
        elif selectedIndex == 4:
            self.execute('xdg-open ' + self.path_base + '/settings.txt')
        else:
            sys.exit()
