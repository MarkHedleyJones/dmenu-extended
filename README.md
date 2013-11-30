# dmenu-extended

An extension to dmenu for quickly opening files and folders.

## Installation

dmenu-extended requires that dmenu is installed. While dmenu-extended works with older versions of dmenu, it is recommended that you donwload and install the latest version of dmenu from http://tools.suckless.org/dmenu to get fuzzy searching.

### Downloading and installing dmenu 4.5

Before executing the following commands make sure you have installed `build-essential` from your package manager.
This can be done on Debian based systems (i.e. Ubuntu, Linux Mint) by executing `sudo apt-get install build-essential`.
  
Copy and paste the following block of code into your terminal to download and install dmenu 4.5
  
  
    cd ~/Downloads && \
    wget http://dl.suckless.org/tools/dmenu-4.5.tar.gz && \
    tar -xzf dmenu-4.5.tar.gz && \
    cd dmenu-4.5 && \
    make && \
    sudo make install && \
    echo "\ndmenu has been installed"
  
  
### Downloading and installing dmenu-extended

Download and extract this repository or copy and paste the following block of code into your terminal.

    cd ~/Downloads && \
    git clone https://github.com/markjones112358/dmenu-extended && \
    cd dmenu-extended && \
    sudo python setup.py install && \
    echo "\ndmenu-extended installation complete"
    
## Running
