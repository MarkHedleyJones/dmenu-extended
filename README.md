# dmenu-extended

An extension to dmenu allowing super fast access to your files, folders, and programs. Install the dmenu_extendedSettings plugin to further extend the menu - adding the ability to download new plugins and manage settings.

# Installation

dmenu-extended requires that dmenu is installed. While dmenu-extended works with older versions of dmenu, it is recommended that you have at least version 4.5 to enable fuzzy searching. If you already have dmenu installed you may [skip this step](#installing-dmenu-extended-this-extension).

## Prerequisite: Installing dmenu

Choose one of the following options to install dmenu

*Which option is best?* - Install using your package manager first - you can update dmenu at any time without breaking anything. If you find that searching isn't as good as it could be (e.g. on Debian) download and install from source.

### Option A: Installing dmenu from your package manager
Installation command to install dmenu on the most popular linux distributions are:

#### Debian, Ubuntu, Linux-Mint

    sudo apt-get install suckless-tools
    
#### Fedora

    sudo yum install dmenu
    
#### Arch

    sudo pacman -S dmenu
    
Once installed, skip to [Installing dmenu-extended](#installing-dmenu-extended-this-extension)
    
### Option B: Installing dmenu from source

Before executing the following commands make sure you have installed `build-essential`, `libx11-dev` and `libxinerama-dev` from your package manager.
This can be done on Debian based systems (i.e. Ubuntu, Linux Mint) by executing the following in a terminal

    sudo apt-get install build-essential libx11-dev libxinerama-dev
  
Then, copy and paste the following block of code into your terminal to download and install dmenu 4.5
  
    cd ~/Downloads && \
    wget http://dl.suckless.org/tools/dmenu-4.5.tar.gz && \
    tar -xzf dmenu-4.5.tar.gz && \
    cd dmenu-4.5 && \
    make && \
    sudo make install && \
    echo "dmenu has been installed"

## Installing dmenu-extended (this extension)

Download and extract this repository or copy and paste the following block of code into your terminal.

    cd ~/Downloads && \
    wget https://github.com/markjones112358/dmenu-extended/archive/master.zip && \
    unzip master.zip && \
    cd dmenu-extended-master && \
    sudo python setup.py install && \
    echo "dmenu-extended installation complete"
    
# Usage

Test that the new menu has been installed by running `dmenu_extended_run` from your terminal. **NOTE:** The first run will be slow as it is set to scan you home folder recursively to build the cache.

The nicest way to enjoy dmenu-extended is to bind the command `dmenu_extended_run` to an easy to reach key-combination. The way in which you do this will be different depending on your desktop environment.

### Ubuntu (Unity), Debian (Gnome)
1. Open **System settings** -> **Keyboard** -> **Shortcuts**
2. Click **Custom shortcuts** and then the **+** to add a new command
3. Enter "dmenu-extended" as the name
4. Enter "dmenu_extended_run" as the command and click apply
5. Click next *disabled*
6. Press the desired combination of keys

### Tiling window managers
If you use a tiling window manager, you may already have a key-combination bound to launch dmenu (i.e. Ctrl+P). Edit your window managers configuration file to launch `dmenu_extended_run` instead.
