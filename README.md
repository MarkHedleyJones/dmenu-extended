# dmenu-extended

An extension to the original [dmenu](http://tools.suckless.org/dmenu/) allowing super fast access to your files, folders, and programs. dmenu-extended has support for plugins, command aliasing, file filtering, and customisation.

## See it in action

<p align="center">
  <img src="https://raw.github.com/markjones112358/dmenu-extended/master/demo.gif" alt="Dmenu-extended demo"/>
</p>

## Dependencies
* **Python**, compatible with versions 2 and 3.
* **dmenu**, preferably version 4.5 or later.

## Installation
Clone this repository *or* download the zip and extract its contents.

You can try dmenu-extended without installation by running `python dmenu_extended.py` from within the extracted folder.

### Global install
Execute `sudo python setup.py install` from within the dmenu-extended directory.

### Local installation
#### Virtualenv
Execute `python setup.py install` from within the dmenu-extended directory
#### Manual
Move both `dmenu_extended.py` and `dmenu_extended_run` into a folder that is in your system path.

*For example*:

Create a folder called bin in your home directory (if you don't already have one)

    mkdir ~/bin
    
Add this folder to your systems `$PATH` variable

    export PATH=$PATH:$HOME/bin
    
Copy the required dmenu-extended files into your local bin folder

    cp ~/Downloads/dmenu-extended-master/dmenu_extended* ~/bin
    
To keep your ~/bin folder on the path after restart, add `export PATH=$PATH:$HOME/bin` to the end of `~/.bash_profile`

# Usage

## Create a keybinding

Test that the new menu has been installed by running `dmenu_extended_run` from your terminal. **NOTE:** The first run will be slow as it is set to scan you home folder recursively to build the cache.

The most productive way to use dmenu-extended is to bind the command `dmenu_extended_run` to an easy to reach key combo. The way in which you do this will be different depending on your desktop environment but here is a brief list.

### Ubuntu (Unity), Debian (Gnome), Mint (Cinnamon)
1. Open **System settings** -> **Keyboard** -> **Shortcuts**
2. Click **Custom shortcuts** and then the **+** (*add custom shortcut*) to add a new command
3. Enter "dmenu_extended" as the name
4. Enter "dmenu_extended_run" as the command and click apply
5. Click next *disabled* (*unassigned*)
6. Press the desired combination of keys (e.g. Alt+Enter)

### Tiling window managers
If you use a tiling window manager, you may already have a key-combination bound to launch dmenu (i.e. Ctrl+P). Edit your window managers configuration file to launch `dmenu_extended_run` instead.

## General Configuration

Menu configuration is contained in a JSON formatted file found at *~/.config/dmenu-extended/config/dmenuExtended_preferences.json* that controls the appearance and functionality of the menu. This file is also accessible from the `-> Menu configuration` submenu as `* Edit menu preferences`

Functions of the items are as follows.

* `"valid_extensions"` list of file extensions of files to include in the cache
* `"watch_folders"` list of base paths to recursively search through for items to include
* `"follow_symlinks"` boolean option controlling whether to follow a link while scanning
* `"ignore_folders"` list of folders to be excluded from the cache
* `"scan_hidden_folders"` boolean value controlling whether to enter hidden folders when scanning
* `"include_hidden_files"` boolean value controlling whether to include hidden files in the cache
* `"include_hidden_folders"` boolean value controlling whether to include hidden folders in the cache
* `"include_items"` list of extra items to include in the cache
* `"exclude_items"` list of items to be excluded from the cache
* `"filter_binaries"` boolean value controlling whether to include binaries that have no corresponding .desktop file
* `"menu"` executable to open the menu (dmenu)
* `"menu_arguments"` list of parameters to launch the menu with
* `"fileopener"` application to handle opening files
* `"filebrowser"` application to handle opening folders
* `"webbrowser"` application to handle opening urls (web browser)
* `"terminal"` terminal emulator application
* `"indicator_submenu"` symbol to indicate a submenu item in the cache
* `"indicator_edit"` symbol to indicate an item will launch an editor in the cache
* `"indicator_alias"` symbol to indicate an aliased command in the cache
 
Adding the item `""` to `"valid_extensions"` will cause files with no extension to be included in the cache.
Adding the item `"*"` to  `"valid_extensions"` will cause **all** files to be included in the cache.

## Rebuild the cache from terminal
It is possible to rebuild the cache from the terminal by running:

    python -c "import dmenu_extended
    dmenu_extended.dmenu().cache_build()"
  
Alternatively, create a python script containing the following lines:

    #! /bin/python
    import dmenu_extended
    dmenu_extended.dmenu().cache_build()

You could run this script directly to rebuild your cache or call it from [cron](http://en.wikipedia.org/wiki/Cron), or create a [systemd](http://en.wikipedia.org/wiki/Systemd) node to rebuild it periodically in the background.


## Advanced usage
Dmenu-extended understands the following modifier characters:

1. **+** (plus) - Manually add an entry to the cache
2. **-** (minus) - Remove a manually added entry from the cache
3. **:** (colon) - Open with
4. **;** (semi-colon) - Execute in terminal

These modifiers are entered into the menu; examples follow.

### **+** (plus) - Manually add an entry to the cache
If there is something you wish to run that isn't in the menu then you can add it by prepending with a +.

* `+htop;` adds htop to the cache.
* `+libreoffice` adds libreoffice to the cache.
* `+http://youtube.com` adds a link to Youtube to the cache.

Once added these commands are stored in the preferences file (see general configuration) and will persist upon a rebuild of the cache. These items can also be manually edited within this file.

#### Built in support for aliases

In addidion to adding items manually, dmenu_extended allows the addition of a more descriptive label for a stored command.
For instance:
* `+htop;#View running processes` displays as `# View system processes (htop)`
* `+libreoffice --writer#Writer` displays as `# Writer (libreoffice --writer)`
* `+http://youtube.com#Youtube` displays as `#Youtube (http://www.youtube.com)`

### **-** (minus) - Remove a manually added entry from the cache
This applies to items that have previously saved to the store. If the item is not found in the store you will be given the chance to add it.

### **:** (colon) - Open with
There are a few different ways to use the colon operator, summarised by example below. In these examples `gedit` is the name of a text editing application.

* `gedit:` - Use gEdit to open a file. A list of all files and folders will be returned to select from.
* `gedit:.txt` - Use gEdit to open a text file. A *filtered list* containing only text files will be shown to select from.
* `/home/me/Documents/writing.txt:` - Open this file using... Returns a list of applications to launch the given file
* `/home/me/Documents/writing.txt:gedit` - Open this file with gedit.
* `gedit:/home/me/Documents/writing.txt` - Open this file with gedit.

### **;** (semi-colon) - Execute in terminal
Dmenu-extended doesn't know when the application you enter needs to be executed in a terminal window. To tell dmenu-extended to launch the following in a terminal, append a semi-colon to the end. Once the terminal program has exited the terminal will close.

For example,

* `htop;` - Launches htop in a terminal window. Without the semi-colon nothing would happen.
* `alsamixer;` - Launches the ALSA sound volume manager in a terminal. Without the semicolon nothing would happen.

#### Holding the terminal open on exit
By using two semicolons (`;;`) at the end of a command the terminal window will remain open once the executed command has completed. This is useful for running programs like `inxi` that exit on completion. You'll want to use this if you see your program flash up and disappear before you get a chance to see the output.

## Acknowledgements
* **Alad** from the [CrunchBang forums](http://crunchbang.org/forums/viewtopic.php?id=36484) for advise on packaging.
* **Head_on_a_Stick** also from the [CrunchBang forums](http://crunchbang.org/forums/viewtopic.php?id=36484) for advise on packaging.
