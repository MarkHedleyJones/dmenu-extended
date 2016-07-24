#!/bin/sh
# Installs dmenu_extended_cache_build as a systemd service to be executed every 20 minutes

# Process command line arguments
for i in "$@"
do
	case $i in
		-u|--user)
			PER_USER_INSTALL=YES
			shift # past argument=value
			;;
		-d|--uninstall)
			UNINSTALL=YES

	esac
done

if [ "$PER_USER_INSTALL" == "YES" ] ; then
	SCRIPT_PATH=$HOME/.local/share/systemd/user
else
	SCRIPT_PATH=/usr/lib/systemd/user
fi

if [ "$UNINSTALL" == "YES" ]; then
	echo "Uninstalling systemd service in $SCRIPT_PATH..."
	rm -v $SCRIPT_PATH/{update-dmenu-extended-db.service,update-dmenu-extended-db.timer}
	exit
fi

if [ ! -d "$SCRIPT_PATH" ]; then
	echo "Creating directory $SCRIPT_PATH..."
	mkdir -p $SCRIPT_PATH
fi

echo "Installing systemd service in $SCRIPT_PATH..." 
cp -v systemd/{update-dmenu-extended-db.service,update-dmenu-extended-db.timer} $SCRIPT_PATH
