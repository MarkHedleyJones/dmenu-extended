# dmenu-extended

An extension to dmenu allowing super fast access to your files, folders, and programs. Install the dmenu_extendedSettings plugin to further extend the menu - adding the ability to download new plugins and manage settings.

<p align="center">
  <img src="https://raw.github.com/markjones112358/dmenu-extended/master/demo.gif" alt="Dmenu-extended demo"/>
</p>


# Installation

Make sure you have ``curl`` installed first (``sudo apt-get install curl``).

Download and extract the archive (or clone using git). Open a terminal and navigate to the source folder (probably `cd ~/Downloads/dmenu-extended-master`) and run the  following command:

    sudo sh setup.sh
    

## Installing dmenuExtended_settings (recommended)

Installing this extra extension enables rebuilding the cache, easy access to configuration files, and the ability to easily download more plugins from the github hosted repository index.

To install this extension, copy and execute the following commands in a terminal

    cd ~/.config/dmenu-extended/plugins && \
    wget https://gist.github.com/markjones112358/7700097/raw/dmenuExtended_settings.py && \
    dmenu_extended_build && \
    echo "" && \
    echo "Settings plugin installed"
    ;

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

Menu configuration is contained in a JSON formatted file found at *~/.config/dmenu-extended/config/dmenuExtended_preferences.json* that controls the appearance and functionality of the menu.

## Advanced usage
Dmenu-extended understands the following modifier characters:

1. **+** (plus) - Add the following command
2. **-** (minus) - Remove the following command
3. **:** (colon) - Open with
4. **;** (semi-colon) - Execute in terminal
5. **;;** (double semi-colon) - Execute in terminal and hold open on complete

These modifiers are entered into the menu; examples follow.

### **+** (plus) - Add an item to the store
If there is something you wish to run that isn't in the menu then you can add it by prepending with a +.

* `+gksudo shutdown now` will add 'gksudo shutdown now' to the index.
* `+libreoffice` will add libreoffice to the index.

Once added these commands are stored in the preferences file (see general configuration) and will persist upon a rebuild of the cache. These items can also be manually edited within this file.

### **-** (minus) - Remove an item from the store
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

### **;;** (double semi-colon) - Execute in terminal and hold
This is the same as a single semi-colon except once the program has completed the terminal window remains open until the used presses enter. This is useful for things commands like `inxi` that returns to the shell on completion.


## Rebuilding the cache (without dmenuExtended_settings)
Entering 'rebuild cache' into dmenu-extended or executing `dmenu_extended_build` rebuild the cache.
