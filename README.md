# dmenu-extended

An extension to dmenu for quickly opening files and folders.

## Installing dmenu

dmenu-extended requires that dmenu is installed. While dmenu-extended works with older versions of dmenu, it is recommended that you download and install the latest version of dmenu (as described below) to get fuzzy searching. Choose one of the following options to install dmenu

*Which option is best?* - Install using your package manager first - you can update dmenu at any time without breaking anything. If you find that searching isn't as good as it could be (e.g. on Debian) download and install from source.

### Installing dmenu and suckless-tools from your package manager
Installation command to install dmenu on the most popular linux distributions are:

#### Debian, Ubuntu, Linux-Mint

    sudo apt-get install suckless-tools
    
#### Fedora

    sudo yum install dmenu
    
#### Arch

    sudo pacman -S dmenu
    
Once installed, skip to Skip to [Installing dmenu-extended](https://github.com/markjones112358/dmenu-extended/edit/master/README.md#installing-dmenu-extended)
    
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
  
## Installing dmenu-extended

Download and extract this repository or copy and paste the following block of code into your terminal.

    cd ~/Downloads && \
    wget https://github.com/markjones112358/dmenu-extended/archive/master.zip && \
    unzip master.zip && \
    cd dmenu-extended-master && \
    sudo python setup.py install && \
    echo "dmenu-extended installation complete"
    
## Running
