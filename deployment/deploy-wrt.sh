#!/bin/bash

echo "Updating the system"
opkg update
echo "Installing libraries"
opkg install nano
opkg install rsync
opkg install python3
opkg install python3-pip
opkg install python3-netifaces
pip3 install pycryptodome
echo "Preparing directories"
mkdir /opt/hip-vpls/
cd ..
echo "Copying the files"
rsync -rv  hiplib  switchd.py  switchfabric.py /opt/hip-vpls/
echo "Copying the service file"
cd startup
cp hip-vpls /etc/init.d/
chmod +x /etc/init.d/hip-vpls
/etc/init.d/hip-vpls enable
/etc/init.d/hip-vpls start

